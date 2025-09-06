"""
Campaign management service
"""

import queue
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from threading import Lock
from app.models import DatabaseManager, Message
from app.services.whatsapp import WhatsAppService


class CampaignService:
    """Campaign management service"""
    
    def __init__(self, db_manager: DatabaseManager, whatsapp_service: WhatsAppService):
        self.db = db_manager
        self.whatsapp_service = whatsapp_service
        self.message_queue = queue.Queue()
        self.campaign_status = {}
        self.status_lock = Lock()
        self._start_worker()
    
    def start_campaign(self, user_id: int, contacts: List[Dict[str, Any]], 
                      message_template: str, delay: int = 2) -> Dict[str, Any]:
        """Start a new campaign"""
        if not contacts:
            return {'success': False, 'error': 'No contacts provided'}
        
        if not message_template:
            return {'success': False, 'error': 'Message template is required'}
        
        # Initialize campaign status
        with self.status_lock:
            self.campaign_status[user_id] = {
                'status': 'running',
                'total': len(contacts),
                'processed': 0,
                'sent': 0,
                'failed': 0,
                'start_time': time.time(),
                'delay': delay
            }
        
        # Add messages to queue
        for contact in contacts:
            phone = contact['phone']
            name = contact.get('name', 'User')
            
            # Personalize message
            personalized_message = self._personalize_message(message_template, name, phone)
            
            # Add to queue
            task = {
                'user_id': user_id,
                'phone': phone,
                'message': personalized_message,
                'delay': delay
            }
            self.message_queue.put(task)
        
        return {
            'success': True, 
            'message': f'Campaign started! {len(contacts)} messages queued for processing.'
        }
    
    def start_campaign_with_media(self, user_id: int, contacts: List[Dict[str, Any]], 
                                 message_template: str = "", delay: int = 2, 
                                 media_files: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a new campaign with media support"""
        if not contacts:
            return {'success': False, 'error': 'No contacts provided'}
        
        if not message_template and not media_files:
            return {'success': False, 'error': 'Either message or media files are required'}
        
        # Initialize campaign status
        with self.status_lock:
            self.campaign_status[user_id] = {
                'status': 'running',
                'total': len(contacts),
                'processed': 0,
                'sent': 0,
                'failed': 0,
                'start_time': time.time(),
                'delay': delay,
                'has_media': bool(media_files)
            }
        
        # Add messages to queue
        for contact in contacts:
            phone = contact['phone']
            name = contact.get('name', 'User')
            
            # Personalize message if provided
            personalized_message = ""
            if message_template:
                personalized_message = self._personalize_message(message_template, name, phone)
            
            # Add to queue
            task = {
                'user_id': user_id,
                'phone': phone,
                'message': personalized_message,
                'media_files': media_files,
                'delay': delay
            }
            self.message_queue.put(task)
        
        media_info = f" with {len(media_files)} media files" if media_files else ""
        return {
            'success': True, 
            'message': f'Campaign started! {len(contacts)} messages{media_info} queued for processing.'
        }
    
    def get_campaign_progress(self, user_id: int) -> Dict[str, Any]:
        """Get campaign progress for user"""
        with self.status_lock:
            if user_id in self.campaign_status:
                progress = self.campaign_status[user_id].copy()
                
                # Calculate progress percentage
                if progress['total'] > 0:
                    progress['percentage'] = round((progress['processed'] / progress['total']) * 100, 1)
                else:
                    progress['percentage'] = 0
                
                # Calculate ETA
                if progress['processed'] > 0 and progress['status'] == 'running':
                    elapsed = time.time() - progress['start_time']
                    rate = progress['processed'] / elapsed
                    remaining = (progress['total'] - progress['processed']) / rate if rate > 0 else 0
                    progress['eta'] = round(remaining)
                else:
                    progress['eta'] = 0
                
                return progress
            else:
                return {
                    'status': 'none',
                    'processed': 0,
                    'total': 0,
                    'sent': 0,
                    'failed': 0,
                    'percentage': 0,
                    'eta': 0
                }
    
    def stop_campaign(self, user_id: int) -> Dict[str, Any]:
        """Stop active campaign"""
        with self.status_lock:
            if user_id in self.campaign_status:
                self.campaign_status[user_id]['status'] = 'stopped'
                return {'success': True, 'message': 'Campaign stopped'}
            else:
                return {'success': False, 'error': 'No active campaign found'}
    
    def get_recent_messages(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent messages for user"""
        query = """
            SELECT phone, message, timestamp, status 
            FROM messages 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        results = self.db.execute_query(query, (user_id, limit))
        
        messages = []
        for row in results:
            messages.append({
                'contact': row['phone'],
                'message': row['message'][:50] + '...' if len(row['message']) > 50 else row['message'],
                'timestamp': row['timestamp'],
                'status': row['status'] or 'sent'
            })
        
        return messages
    
    def _personalize_message(self, template: str, name: str, phone: str) -> str:
        """Personalize message template with contact data"""
        return template.replace('{name}', name or 'User').replace('{phone}', phone)
    
    def _start_worker(self):
        """Start background worker thread"""
        worker_thread = threading.Thread(target=self._background_worker, daemon=True)
        worker_thread.start()
    
    def _background_worker(self):
        """Background worker to process message queue"""
        while True:
            try:
                # Get task from queue (blocks until available)
                task = self.message_queue.get(timeout=1)
                
                user_id = task['user_id']
                phone = task['phone']
                message = task['message']
                media_files = task.get('media_files')
                delay = task.get('delay', 2)
                
                # Check if campaign is still running
                with self.status_lock:
                    if (user_id in self.campaign_status and 
                        self.campaign_status[user_id]['status'] != 'running'):
                        # Campaign stopped, skip this message
                        self.message_queue.task_done()
                        continue
                
                try:
                    # Get user and send message
                    from app.models import User
                    user = User.get_by_id(self.db, user_id)
                    
                    if user:
                        # Send message with or without media
                        if media_files:
                            result = self.whatsapp_service.send_message_with_multiple_media(
                                user, phone, message, media_files
                            )
                        else:
                            result = self.whatsapp_service.send_message(user, phone, message)
                        
                        # Update campaign status
                        with self.status_lock:
                            if user_id in self.campaign_status:
                                if result['success']:
                                    self.campaign_status[user_id]['sent'] += 1
                                    # Log successful message with media info
                                    log_message = message
                                    if media_files:
                                        log_message = f"[Media: {len(media_files)} files] {message}"
                                    self._log_message(user_id, phone, log_message, 'sent')
                                    # Update contact status
                                    self._update_contact_status(user_id, phone, 'sent')
                                else:
                                    self.campaign_status[user_id]['failed'] += 1
                                    print(f"Failed to send message to {phone}: {result.get('error', 'Unknown error')}")
                                
                                self.campaign_status[user_id]['processed'] += 1
                                
                                # Check if campaign is complete
                                if (self.campaign_status[user_id]['processed'] >= 
                                    self.campaign_status[user_id]['total']):
                                    self.campaign_status[user_id]['status'] = 'completed'
                    
                except Exception as e:
                    print(f"Error processing message for {phone}: {str(e)}")
                    with self.status_lock:
                        if user_id in self.campaign_status:
                            self.campaign_status[user_id]['failed'] += 1
                            self.campaign_status[user_id]['processed'] += 1
                
                # Mark task as done
                self.message_queue.task_done()
                
                # Add delay between messages
                time.sleep(delay)
                
            except queue.Empty:
                # No tasks in queue, continue loop
                continue
            except Exception as e:
                print(f"Background worker error: {str(e)}")
    
    def _log_message(self, user_id: int, phone: str, message: str, status: str):
        """Log message to database"""
        try:
            msg = Message(self.db)
            msg.user_id = user_id
            msg.phone = phone
            msg.message = message
            msg.status = status
            msg.save()
        except Exception as e:
            print(f"Error logging message: {str(e)}")
    
    def _update_contact_status(self, user_id: int, phone: str, status: str):
        """Update contact status"""
        try:
            query = "UPDATE contacts SET status = ? WHERE phone = ? AND user_id = ?"
            self.db.execute_update(query, (status, phone, user_id))
        except Exception as e:
            print(f"Error updating contact status: {str(e)}")
