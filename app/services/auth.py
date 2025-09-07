"""
Authentication service for user management
"""

import hashlib
import secrets
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.models import DatabaseManager, User


class AuthService:
    """Authentication service"""
    
    def __init__(self, db_manager: DatabaseManager, evolution_api_url: str, evolution_global_key: str):
        self.db = db_manager
        self.evolution_api_url = evolution_api_url
        self.evolution_global_key = evolution_global_key
    
    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2"""
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{key.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, key = password_hash.split(':')
            return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex() == key
        except Exception:
            return False
    
    def create_user(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """Create a new user with Evolution API instance"""
        try:
            # Check if user already exists
            if User.get_by_email(self.db, email):
                return {'success': False, 'error': 'Email already registered'}
            
            # Create user instance
            user = User(self.db)
            user.name = name
            user.email = email
            user.password_hash = self.hash_password(password)
            
            # Generate unique instance name
            timestamp_part = str(int(time.time()))[-6:]
            user.evolution_instance_name = f"user{timestamp_part}"
            
            # Save user to get ID
            if not user.save():
                return {'success': False, 'error': 'Failed to create user'}
            
            # Create Evolution API instance
            instance_result = self._create_evolution_instance(user)
            
            if instance_result['success']:
                user.evolution_api_key = instance_result['api_key']
                user.instance_created = True
                user.save()
                return {'success': True, 'user_id': user.id, 'instance_name': user.evolution_instance_name}
            else:
                # Rollback user creation if instance creation failed
                user.delete()
                return {'success': False, 'error': f"Failed to create Evolution instance: {instance_result['error']}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = User.get_by_email(self.db, email)
        if user and self.verify_password(password, user.password_hash):
            self._update_last_login(user)
            return user
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.get_by_id(self.db, user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return User.get_by_email(self.db, email)
    
    def create_reset_token(self, user_id: int) -> str:
        """Create password reset token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        
        query = """
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        """
        self.db.execute_insert(query, (user_id, token, expires_at))
        return token
    
    def verify_reset_token(self, token: str) -> Optional[int]:
        """Verify password reset token and return user_id"""
        query = """
            SELECT user_id FROM password_reset_tokens 
            WHERE token = ? AND expires_at > ? AND used = FALSE
        """
        result = self.db.execute_query(query, (token, datetime.now()))
        return result[0]['user_id'] if result else None
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        user = User.get_by_id(self.db, user_id)
        if user:
            user.password_hash = self.hash_password(new_password)
            return user.save()
        return False
    
    def mark_reset_token_used(self, token: str) -> bool:
        """Mark reset token as used"""
        query = "UPDATE password_reset_tokens SET used = TRUE WHERE token = ?"
        return self.db.execute_update(query, (token,)) > 0
    
    def create_session(self, user_id: int, remember_me: bool = False) -> str:
        """Create user session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=30 if remember_me else 1)
        
        query = """
            INSERT INTO user_sessions (user_id, session_id, expires_at, remember_me)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_insert(query, (user_id, session_id, expires_at, remember_me))
        return session_id
    
    def verify_session(self, session_id: str) -> Optional[int]:
        """Verify user session and return user_id"""
        query = """
            SELECT user_id FROM user_sessions 
            WHERE session_id = ? AND expires_at > ?
        """
        result = self.db.execute_query(query, (session_id, datetime.now()))
        return result[0]['user_id'] if result else None
    
    def delete_session(self, user_id: int):
        """Delete user sessions"""
        query = "DELETE FROM user_sessions WHERE user_id = ?"
        self.db.execute_update(query, (user_id,))
    
    def _create_evolution_instance(self, user: User) -> Dict[str, Any]:
        """Create Evolution API instance for user"""
        try:
            response = requests.post(
                f"{self.evolution_api_url}/instance/create",
                headers={
                    'Content-Type': 'application/json',
                    'apikey': self.evolution_global_key
                },
                json={'instanceName': user.evolution_instance_name, 'integration': 'WHATSAPP-BAILEYS'},
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                # Try both old and new API response formats
                api_key = result.get('hash', '') or result.get('instance', {}).get('token', '')
                return {'success': True, 'api_key': api_key}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _update_last_login(self, user: User):
        """Update user's last login time"""
        user.last_login = datetime.now()
        user.save()
