"""
WhatsApp service for Evolution API integration
"""

import requests
from typing import Dict, Any, Optional
from app.models import User, DatabaseManager


class WhatsAppService:
    """WhatsApp service for Evolution API integration"""
    
    def __init__(self, evolution_api_url: str, evolution_global_key: str):
        self.evolution_api_url = evolution_api_url
        self.evolution_global_key = evolution_global_key
    
    def get_qr_code(self, user: User) -> Dict[str, Any]:
        """Get QR code for user's WhatsApp connection"""
        if not user or not user.evolution_instance_name:
            return {'success': False, 'error': 'User or instance not found'}
        
        try:
            response = requests.get(
                f"{self.evolution_api_url}/instance/connect/{user.evolution_instance_name}",
                headers={'apikey': self.evolution_global_key},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                qr_code_raw = result.get('base64', '')
                
                # Remove the data:image/png;base64, prefix if present
                if qr_code_raw.startswith('data:image/png;base64,'):
                    qr_code = qr_code_raw.replace('data:image/png;base64,', '')
                else:
                    qr_code = qr_code_raw
                
                # Update QR code in user model
                user.qr_code = qr_code
                user.save()
                
                return {'success': True, 'qr_code': qr_code}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_connection_status(self, user: User) -> Dict[str, Any]:
        """Check WhatsApp connection status"""
        if not user or not user.evolution_instance_name:
            return {'success': False, 'error': 'User or instance not found', 'connected': False}
        
        try:
            response = requests.get(
                f"{self.evolution_api_url}/instance/connectionState/{user.evolution_instance_name}",
                headers={'apikey': user.evolution_api_key or self.evolution_global_key},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('instance', {}).get('state', 'disconnected')
                
                # Update status in user model
                whatsapp_connected = status == 'open'
                user.connection_status = status
                user.whatsapp_connected = whatsapp_connected
                user.save()
                
                return {
                    'success': True, 
                    'status': status, 
                    'connected': whatsapp_connected
                }
            else:
                return {
                    'success': False, 
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'connected': False
                }
                
        except Exception as e:
            return {
                'success': False, 
                'error': str(e),
                'connected': False
            }
    
    def send_message(self, user: User, phone: str, message: str) -> Dict[str, Any]:
        """Send text message via WhatsApp"""
        if not user or not user.evolution_instance_name:
            return {'success': False, 'error': 'User or instance not found'}
        
        if not phone or not message:
            return {'success': False, 'error': 'Phone number and message are required'}
        
        try:
            response = requests.post(
                f"{self.evolution_api_url}/message/sendText/{user.evolution_instance_name}",
                headers={
                    'Content-Type': 'application/json',
                    'apikey': self.evolution_global_key
                },
                json={
                    'number': phone,
                    'textMessage': {'text': message}
                },
                timeout=30
            )
            
            if response.status_code == 201:
                return {'success': True, 'message': 'Message sent successfully'}
            else:
                return {
                    'success': False, 
                    'error': f"Failed to send message: HTTP {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {'success': False, 'error': f"Error sending message: {str(e)}"}
    
    def send_media(self, user: User, phone: str, media_data: str, caption: str = "", media_type: str = "image") -> Dict[str, Any]:
        """Send media (image/video) via WhatsApp using Evolution API"""
        if not user or not user.evolution_instance_name:
            return {'success': False, 'error': 'User or instance not found'}
        
        if not phone:
            return {'success': False, 'error': 'Phone number is required'}
        
        if not media_data:
            return {'success': False, 'error': 'Media data is required'}
        
        try:
            # Clean up media data - Evolution API expects just base64 string without data: prefix
            if media_data.startswith('data:'):
                # Extract just the base64 part after the comma
                base64_data = media_data.split(',', 1)[1] if ',' in media_data else media_data
            else:
                base64_data = media_data
            
            # Determine the endpoint and payload based on media type
            endpoint = f"{self.evolution_api_url}/message/sendMedia/{user.evolution_instance_name}"
            
            if media_type.lower() in ['image', 'photo', 'img']:
                media_payload = {
                    'number': phone,
                    'mediaMessage': {
                        'mediatype': 'image',
                        'media': base64_data,
                        'caption': caption
                    }
                }
            elif media_type.lower() in ['video', 'vid']:
                media_payload = {
                    'number': phone,
                    'mediaMessage': {
                        'mediatype': 'video',
                        'media': base64_data,
                        'caption': caption
                    }
                }
            else:
                return {'success': False, 'error': 'Unsupported media type. Use image or video.'}
            
            response = requests.post(
                endpoint,
                headers={
                    'Content-Type': 'application/json',
                    'apikey': self.evolution_global_key
                },
                json=media_payload,
                timeout=60  # Longer timeout for media uploads
            )
            
            if response.status_code == 201:
                return {'success': True, 'message': f'Media {media_type} sent successfully'}
            else:
                return {
                    'success': False, 
                    'error': f"Failed to send media: HTTP {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {'success': False, 'error': f"Error sending media: {str(e)}"}
    
    def send_multiple_media(self, user: User, phone: str, media_files: list, caption: str = "") -> Dict[str, Any]:
        """Send multiple media files via WhatsApp"""
        if not user or not user.evolution_instance_name:
            return {'success': False, 'error': 'User or instance not found'}
        
        if not phone:
            return {'success': False, 'error': 'Phone number is required'}
        
        if not media_files:
            return {'success': False, 'error': 'No media files provided'}
        
        results = []
        successful_sends = 0
        
        try:
            for i, media_file in enumerate(media_files):
                # For the first media, include the caption
                file_caption = caption if i == 0 else ""
                
                result = self.send_media(
                    user, 
                    phone, 
                    media_file['base64'], 
                    file_caption, 
                    media_file['media_type']
                )
                
                results.append({
                    'filename': media_file['filename'],
                    'success': result['success'],
                    'message': result.get('message', ''),
                    'error': result.get('error', '')
                })
                
                if result['success']:
                    successful_sends += 1
                else:
                    # If a media file fails, log but continue with others
                    pass
                
                # Small delay between media files to avoid rate limiting
                import time
                time.sleep(1)
            
            if successful_sends == len(media_files):
                return {
                    'success': True, 
                    'message': f'All {successful_sends} media files sent successfully',
                    'results': results
                }
            elif successful_sends > 0:
                return {
                    'success': True, 
                    'message': f'{successful_sends} of {len(media_files)} media files sent successfully',
                    'results': results
                }
            else:
                return {
                    'success': False, 
                    'error': f'Failed to send all {len(media_files)} media files',
                    'results': results
                }
                
        except Exception as e:
            return {'success': False, 'error': f"Error sending multiple media: {str(e)}"}
    
    def send_message_with_multiple_media(self, user: User, phone: str, message: str = "", media_files: list = None) -> Dict[str, Any]:
        """Send message with multiple media attachments"""
        if media_files:
            return self.send_multiple_media(user, phone, media_files, message)
        elif message:
            return self.send_message(user, phone, message)
        else:
            return {'success': False, 'error': 'Either message or media files are required'}
        """Send message with optional media attachment"""
        results = []
        
        # Send media first if provided
        if media_data:
            media_result = self.send_media(user, phone, media_data, message, media_type)
            results.append(media_result)
            
            if not media_result['success']:
                return media_result
        else:
            # Send text message if no media
            if message:
                text_result = self.send_message(user, phone, message)
                results.append(text_result)
                
                if not text_result['success']:
                    return text_result
        
        return {'success': True, 'message': 'Message sent successfully', 'results': results}
    
    def delete_instance(self, user: User) -> Dict[str, Any]:
        """Delete Evolution API instance"""
        if not user or not user.evolution_instance_name:
            return {'success': True}  # Nothing to delete
        
        try:
            response = requests.delete(
                f"{self.evolution_api_url}/instance/delete/{user.evolution_instance_name}",
                headers={'apikey': user.evolution_api_key or self.evolution_global_key},
                timeout=30
            )
            
            if response.status_code in [200, 404]:  # 404 means already deleted
                return {'success': True}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
