"""
Contact management service
"""

import csv
import io
from typing import List, Dict, Any, Optional, Tuple
from app.models import DatabaseManager, Contact, Message


class ContactService:
    """Contact management service"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_contacts(self, user_id: int, page: int = 1, per_page: int = 20, 
                    search: str = None) -> Dict[str, Any]:
        """Get paginated contacts for user"""
        offset = (page - 1) * per_page
        
        # Get contacts with message status
        contacts = self._get_contacts_with_status(user_id, per_page, offset, search)
        
        # Get total count
        total_contacts = Contact.count_by_user(self.db, user_id, search)
        total_pages = (total_contacts + per_page - 1) // per_page
        
        return {
            'contacts': contacts,
            'page': page,
            'per_page': per_page,
            'total_contacts': total_contacts,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
    
    def get_contact_stats(self, user_id: int) -> Dict[str, Any]:
        """Get contact statistics for user"""
        # Total contacts
        total_query = "SELECT COUNT(*) as count FROM contacts WHERE user_id = ?"
        total_result = self.db.execute_query(total_query, (user_id,))
        total = total_result[0]['count'] if total_result else 0
        
        # Messages sent count (unique phones)
        sent_query = """
            SELECT COUNT(DISTINCT phone) as count 
            FROM messages 
            WHERE user_id = ?
        """
        sent_result = self.db.execute_query(sent_query, (user_id,))
        sent = sent_result[0]['count'] if sent_result else 0
        
        # Pending contacts (not in messages table)
        pending_query = """
            SELECT COUNT(*) as count 
            FROM contacts c 
            WHERE c.user_id = ? 
            AND c.phone NOT IN (
                SELECT DISTINCT phone 
                FROM messages 
                WHERE user_id = ?
            )
        """
        pending_result = self.db.execute_query(pending_query, (user_id, user_id))
        pending = pending_result[0]['count'] if pending_result else 0
        
        # Failed contacts (for future use)
        failed_query = "SELECT COUNT(*) as count FROM contacts WHERE user_id = ? AND status = 'failed'"
        failed_result = self.db.execute_query(failed_query, (user_id,))
        failed = failed_result[0]['count'] if failed_result else 0
        
        # Total messages sent by user
        total_messages_query = "SELECT COUNT(*) as count FROM messages WHERE user_id = ?"
        total_messages_result = self.db.execute_query(total_messages_query, (user_id,))
        total_messages = total_messages_result[0]['count'] if total_messages_result else 0
        
        # Messages sent today
        today_messages_query = """
            SELECT COUNT(*) as count FROM messages 
            WHERE user_id = ? AND DATE(timestamp) = DATE('now')
        """
        today_messages_result = self.db.execute_query(today_messages_query, (user_id,))
        messages_today = today_messages_result[0]['count'] if today_messages_result else 0
        
        # Contacts added this week (approximate - using existing data)
        contacts_this_week = 0  # Would need created_at column for accurate count
        
        return {
            'total': total,
            'pending': pending,
            'sent': sent,
            'failed': failed,
            'total_messages': total_messages,
            'messages_today': messages_today,
            'contacts_this_week': contacts_this_week
        }
    
    def add_contact(self, user_id: int, name: str, phone: str) -> Dict[str, Any]:
        """Add a single contact"""
        if not name or not phone:
            return {'success': False, 'error': 'Name and phone are required'}
        
        contact = Contact(self.db)
        contact.user_id = user_id
        contact.name = name.strip()
        contact.phone = phone.strip()
        contact.status = 'pending'
        
        if contact.save():
            return {'success': True, 'message': 'Contact added successfully'}
        else:
            return {'success': False, 'error': 'Contact already exists or failed to save'}
    
    def update_contact(self, contact_id: int, user_id: int, name: str, phone: str) -> Dict[str, Any]:
        """Update a contact"""
        if not name or not phone:
            return {'success': False, 'error': 'Name and phone are required'}
        
        # Get contact and verify ownership
        contacts = self.db.execute_query(
            "SELECT * FROM contacts WHERE id = ? AND user_id = ?", 
            (contact_id, user_id)
        )
        
        if not contacts:
            return {'success': False, 'error': 'Contact not found'}
        
        # Update contact
        query = "UPDATE contacts SET name = ?, phone = ? WHERE id = ? AND user_id = ?"
        rows_affected = self.db.execute_update(query, (name.strip(), phone.strip(), contact_id, user_id))
        
        if rows_affected > 0:
            return {'success': True, 'message': 'Contact updated successfully'}
        else:
            return {'success': False, 'error': 'Failed to update contact'}
    
    def delete_contact(self, contact_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a single contact"""
        query = "DELETE FROM contacts WHERE id = ? AND user_id = ?"
        rows_affected = self.db.execute_update(query, (contact_id, user_id))
        
        if rows_affected > 0:
            return {'success': True, 'message': 'Contact deleted successfully'}
        else:
            return {'success': False, 'error': 'Contact not found'}
    
    def delete_contacts(self, contact_ids: List[int], user_id: int) -> Dict[str, Any]:
        """Delete multiple contacts"""
        if not contact_ids:
            return {'success': False, 'error': 'No contacts selected'}
        
        # Build query with placeholders
        placeholders = ','.join('?' * len(contact_ids))
        query = f"DELETE FROM contacts WHERE id IN ({placeholders}) AND user_id = ?"
        params = contact_ids + [user_id]
        
        rows_affected = self.db.execute_update(query, tuple(params))
        
        if rows_affected > 0:
            return {'success': True, 'message': f'{rows_affected} contacts deleted successfully'}
        else:
            return {'success': False, 'error': 'No contacts were deleted'}
    
    def import_from_csv(self, user_id: int, csv_content: str) -> Dict[str, Any]:
        """Import contacts from CSV content"""
        try:
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            added_count = 0
            duplicate_count = 0
            error_count = 0
            
            for row in csv_reader:
                name = row.get('name', '').strip()
                phone = row.get('phone', '').strip()
                
                if name and phone:
                    result = self.add_contact(user_id, name, phone)
                    if result['success']:
                        added_count += 1
                    else:
                        if 'already exists' in result.get('error', ''):
                            duplicate_count += 1
                        else:
                            error_count += 1
                else:
                    error_count += 1
            
            return {
                'success': True,
                'message': f'Import completed. Added: {added_count}, Duplicates: {duplicate_count}, Errors: {error_count}',
                'stats': {
                    'added': added_count,
                    'duplicates': duplicate_count,
                    'errors': error_count
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to import CSV: {str(e)}'}
    
    def get_contacts_for_campaign(self, user_id: int, recipient_type: str, 
                                selected_contacts: List[str] = None) -> List[Dict[str, Any]]:
        """Get contacts for campaign based on recipient type"""
        if recipient_type == 'selected' and selected_contacts:
            # Get selected contacts
            placeholders = ','.join('?' * len(selected_contacts))
            query = f"""
                SELECT phone, name FROM contacts 
                WHERE phone IN ({placeholders}) AND user_id = ?
            """
            params = selected_contacts + [user_id]
            
        elif recipient_type == 'pending':
            # Get contacts that haven't been sent messages
            query = """
                SELECT phone, name FROM contacts 
                WHERE user_id = ? 
                AND phone NOT IN (
                    SELECT DISTINCT phone 
                    FROM messages 
                    WHERE user_id = ?
                )
            """
            params = [user_id, user_id]
            
        else:  # 'all'
            # Get all contacts
            query = "SELECT phone, name FROM contacts WHERE user_id = ?"
            params = [user_id]
        
        results = self.db.execute_query(query, tuple(params))
        return [{'phone': r['phone'], 'name': r['name']} for r in results]
    
    def _get_contacts_with_status(self, user_id: int, limit: int, offset: int, 
                                 search: str = None) -> List[Dict[str, Any]]:
        """Get contacts with message status"""
        query = """
            SELECT c.id, c.name, c.phone, c.status,
                   CASE 
                       WHEN m.phone IS NOT NULL THEN 'sent'
                       ELSE 'pending'
                   END as actual_status,
                   MAX(m.timestamp) as last_sent
            FROM contacts c
            LEFT JOIN messages m ON c.phone = m.phone AND c.user_id = m.user_id
            WHERE c.user_id = ?
        """
        params = [user_id]
        
        if search:
            query += " AND (c.name LIKE ? OR c.phone LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        query += " GROUP BY c.id, c.name, c.phone, c.status ORDER BY c.name ASC, c.id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        results = self.db.execute_query(query, tuple(params))
        
        contacts = []
        for row in results:
            contacts.append({
                'id': row['id'],
                'name': row['name'],
                'phone': row['phone'],
                'status': row['actual_status'],
                'last_sent': row['last_sent'] if row['last_sent'] else 'Never'
            })
        
        return contacts
