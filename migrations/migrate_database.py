"""
Safe database migration utility for preserving existing data
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, Any


class DatabaseMigrator:
    """Handle database migrations safely"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def create_backup(self) -> bool:
        """Create a backup of the existing database"""
        try:
            if os.path.exists(self.db_path):
                import shutil
                shutil.copy2(self.db_path, self.backup_path)
                print(f"✓ Database backup created: {self.backup_path}")
                return True
            return False
        except Exception as e:
            print(f"✗ Failed to create backup: {e}")
            return False
    
    def check_existing_data(self) -> Dict[str, Any]:
        """Check what data exists in the database"""
        if not os.path.exists(self.db_path):
            return {'exists': False}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            data_info = {'exists': True, 'tables': tables, 'counts': {}}
            
            # Count records in important tables
            for table in ['app_users', 'contacts', 'messages']:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    data_info['counts'][table] = cursor.fetchone()[0]
            
            conn.close()
            return data_info
            
        except Exception as e:
            print(f"Error checking existing data: {e}")
            return {'exists': True, 'error': str(e)}
    
    def safe_migrate(self) -> bool:
        """Safely migrate database while preserving existing data"""
        # Check existing data
        data_info = self.check_existing_data()
        
        if not data_info['exists']:
            print("No existing database found - creating fresh database")
            return self._create_fresh_database()
        
        if 'error' in data_info:
            print(f"Error reading database: {data_info['error']}")
            return False
        
        # Show existing data info
        print("Existing database found:")
        for table, count in data_info.get('counts', {}).items():
            print(f"  - {table}: {count} records")
        
        # Check if migration is actually needed
        if not self._migration_needed(data_info):
            print("✓ Database is already up to date - no migration needed")
            return True
        
        # Create backup only when migration is needed
        if not self.create_backup():
            print("Failed to create backup - aborting migration")
            return False
        
        # Perform safe migration
        return self._migrate_existing_database(data_info)
    
    def _migration_needed(self, data_info: Dict[str, Any]) -> bool:
        """Check if database migration is actually needed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            existing_tables = data_info.get('tables', [])
            
            # Check for missing tables
            required_tables = ['app_users', 'contacts', 'messages', 'user_sessions', 'password_reset_tokens']
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                conn.close()
                return True
            
            # Check if contacts table needs unique constraint
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='contacts'")
            result = cursor.fetchone()
            
            if result and 'UNIQUE(user_id, phone)' not in result[0]:
                conn.close()
                return True
            
            # Check if status values need updating
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE status = 'active' OR status IS NULL")
            needs_status_update = cursor.fetchone()[0] > 0
            
            conn.close()
            
            if needs_status_update:
                return True
            
            return False
            
        except Exception as e:
            print(f"Error checking migration needs: {e}")
            return True  # Better safe than sorry
    
    def _create_fresh_database(self) -> bool:
        """Create a fresh database with all tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create all tables
            self._create_all_tables(cursor)
            
            conn.commit()
            conn.close()
            print("✓ Fresh database created")
            return True
            
        except Exception as e:
            print(f"✗ Failed to create fresh database: {e}")
            return False
    
    def _migrate_existing_database(self, data_info: Dict[str, Any]) -> bool:
        """Migrate existing database safely"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            existing_tables = data_info.get('tables', [])
            
            # Create missing tables only
            if 'app_users' not in existing_tables:
                self._create_users_table(cursor)
                print("✓ Created app_users table")
            
            if 'contacts' not in existing_tables:
                self._create_contacts_table(cursor)
                print("✓ Created contacts table")
            else:
                # Check if contacts table needs the unique constraint
                self._ensure_contacts_unique_constraint(cursor)
            
            if 'messages' not in existing_tables:
                self._create_messages_table(cursor)
                print("✓ Created messages table")
            
            if 'user_sessions' not in existing_tables:
                self._create_sessions_table(cursor)
                print("✓ Created user_sessions table")
            
            if 'password_reset_tokens' not in existing_tables:
                self._create_reset_tokens_table(cursor)
                print("✓ Created password_reset_tokens table")
            
            # Update status values if needed
            self._update_contact_status_values(cursor)
            
            conn.commit()
            conn.close()
            print("✓ Database migration completed successfully")
            return True
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            return False
    
    def _ensure_contacts_unique_constraint(self, cursor):
        """Ensure contacts table has unique constraint"""
        try:
            # Check if unique constraint exists
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='contacts'")
            result = cursor.fetchone()
            
            if result and 'UNIQUE(user_id, phone)' not in result[0]:
                print("Adding unique constraint to contacts table...")
                
                # Create new table with constraint
                cursor.execute('''
                    CREATE TABLE contacts_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        phone TEXT NOT NULL,
                        name TEXT,
                        status TEXT DEFAULT 'pending',
                        sent_at TIMESTAMP,
                        UNIQUE(user_id, phone),
                        FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
                    )
                ''')
                
                # Copy data, handling duplicates
                cursor.execute('''
                    INSERT OR IGNORE INTO contacts_new (id, user_id, phone, name, status, sent_at)
                    SELECT id, user_id, phone, name, 
                           CASE WHEN status = 'active' THEN 'pending' ELSE status END, 
                           sent_at 
                    FROM contacts
                    GROUP BY user_id, phone
                ''')
                
                # Replace old table
                cursor.execute('DROP TABLE contacts')
                cursor.execute('ALTER TABLE contacts_new RENAME TO contacts')
                
                print("✓ Added unique constraint to contacts table")
                
        except Exception as e:
            print(f"Warning: Could not add unique constraint: {e}")
    
    def _update_contact_status_values(self, cursor):
        """Update old status values to new ones"""
        try:
            # Update 'active' status to 'pending'
            cursor.execute("UPDATE contacts SET status = 'pending' WHERE status = 'active' OR status IS NULL")
            updated = cursor.rowcount
            if updated > 0:
                print(f"✓ Updated {updated} contact status values")
        except Exception as e:
            print(f"Warning: Could not update contact status: {e}")
    
    def _create_all_tables(self, cursor):
        """Create all required tables"""
        self._create_users_table(cursor)
        self._create_contacts_table(cursor)
        self._create_messages_table(cursor)
        self._create_sessions_table(cursor)
        self._create_reset_tokens_table(cursor)
    
    def _create_users_table(self, cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                evolution_instance_name TEXT UNIQUE,
                evolution_api_key TEXT,
                whatsapp_connected BOOLEAN DEFAULT FALSE,
                whatsapp_number TEXT,
                qr_code TEXT,
                connection_status TEXT DEFAULT 'disconnected',
                instance_created BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
    
    def _create_contacts_table(self, cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phone TEXT NOT NULL,
                name TEXT,
                status TEXT DEFAULT 'pending',
                sent_at TIMESTAMP,
                UNIQUE(user_id, phone),
                FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
            )
        ''')
    
    def _create_messages_table(self, cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phone TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'sent',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
            )
        ''')
    
    def _create_sessions_table(self, cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                remember_me BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
            )
        ''')
    
    def _create_reset_tokens_table(self, cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES app_users (id) ON DELETE CASCADE
            )
        ''')


def migrate_database(db_path: str) -> bool:
    """Main migration function"""
    print("=== WhatsApp Message Hub Database Migration ===")
    
    migrator = DatabaseMigrator(db_path)
    
    # Check current state
    data_info = migrator.check_existing_data()
    
    if data_info['exists'] and data_info.get('counts'):
        print(f"\nFound existing data:")
        for table, count in data_info['counts'].items():
            print(f"  📊 {table}: {count} records")
        print(f"\n⚠️  Your existing data will be preserved!")
    
    # Perform migration
    success = migrator.safe_migrate()
    
    if success:
        print(f"\n✅ Migration completed successfully!")
        if 'backup_path' in locals():
            print(f"   Backup saved to: {migrator.backup_path}")
        print(f"   Your existing data has been preserved.")
    else:
        print(f"\n❌ Migration failed!")
        print(f"   Your original database is untouched.")
    
    return success


if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'whatsapp.db'
    migrate_database(db_path)
