"""
Migration script to backup old application and prepare for new structure
"""

import os
import shutil
import sqlite3
from datetime import datetime


def create_backup():
    """Create backup of current files"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Creating backup in {backup_dir}/")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files to backup
    files_to_backup = [
        'app_multiuser.py',
        'user_auth.py', 
        'config.py',
        'auth.py',
        'auth_integration.py'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"Backed up: {file}")
    
    # Backup database
    if os.path.exists('whatsapp.db'):
        shutil.copy2('whatsapp.db', backup_dir)
        print("Backed up: whatsapp.db")
    
    print(f"Backup completed in {backup_dir}/")
    return backup_dir


def check_database_compatibility():
    """Check if existing database is compatible"""
    if not os.path.exists('whatsapp.db'):
        print("No existing database found - fresh installation")
        return True
    
    try:
        conn = sqlite3.connect('whatsapp.db')
        cursor = conn.cursor()
        
        # Check for required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['app_users', 'contacts', 'messages']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
            print("Database migration may be required")
        else:
            print("Database appears compatible")
        
        conn.close()
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"Database check failed: {e}")
        return False


def verify_new_structure():
    """Verify the new application structure is in place"""
    required_dirs = [
        'app',
        'app/models',
        'app/services', 
        'app/routes',
        'app/utils'
    ]
    
    required_files = [
        'app/__init__.py',
        'app/config.py',
        'app/models/__init__.py',
        'app/services/__init__.py',
        'app/routes/__init__.py',
        'app/utils/__init__.py',
        'run.py'
    ]
    
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_dirs:
        print(f"Missing directories: {missing_dirs}")
        return False
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    
    print("New application structure verified ✓")
    return True


def show_migration_status():
    """Show current migration status"""
    print("\n" + "="*50)
    print("MIGRATION STATUS")
    print("="*50)
    
    # Check old files
    old_files = ['app_multiuser.py', 'user_auth.py']
    old_exists = [f for f in old_files if os.path.exists(f)]
    
    if old_exists:
        print(f"Old files present: {old_exists}")
        print("Status: MIGRATION NEEDED")
    else:
        print("Old files: NOT FOUND")
    
    # Check new structure
    new_structure = verify_new_structure()
    if new_structure:
        print("New structure: READY")
    else:
        print("New structure: INCOMPLETE")
    
    # Check database
    db_compatible = check_database_compatibility()
    if db_compatible:
        print("Database: COMPATIBLE")
    else:
        print("Database: NEEDS MIGRATION")
    
    print("="*50)
    
    # Recommendations
    if old_exists and new_structure:
        print("\nRECOMMENDATION:")
        print("1. Test the new application: python run.py")
        print("2. If working correctly, remove old files")
        print("3. Update your deployment scripts")
    elif old_exists:
        print("\nRECOMMENDATION:")
        print("Complete the restructuring process first")
    else:
        print("\nSTATUS: Migration appears complete!")


if __name__ == '__main__':
    print("WhatsApp Message Hub - Migration Helper")
    print("This script helps migrate from the old single-file structure")
    print("to the new modular architecture.\n")
    
    # Create backup
    backup_dir = create_backup()
    
    # Check current status
    show_migration_status()
    
    print(f"\nBackup created in: {backup_dir}")
    print("\nNext steps:")
    print("1. Test the new application: python run.py")
    print("2. Verify all functionality works")
    print("3. Update your .env configuration")
    print("4. Remove old files when satisfied")
