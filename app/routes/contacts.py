"""
Contact management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app

from app.models import DatabaseManager
from app.services.contact import ContactService
from app.utils.auth import login_required, get_current_user, whatsapp_setup_required
from app.utils.validators import validate_csv_file, sanitize_csv_content, sanitize_input

contacts_bp = Blueprint('contacts', __name__)


def get_contact_service():
    """Get contact service instance"""
    db_manager = DatabaseManager(current_app.config['DB_PATH'])
    return ContactService(db_manager)


@contacts_bp.route('/')
@login_required
@whatsapp_setup_required
def list_contacts():
    """List contacts with pagination"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 20
    search = request.args.get('search', '').strip()
    
    # Get contacts and stats
    contact_service = get_contact_service()
    contacts_data = contact_service.get_contacts(user.id, page, per_page, search)
    stats = contact_service.get_contact_stats(user.id)
    
    return render_template('contacts_list.html',
                         **contacts_data,
                         user=user,
                         stats=stats,
                         search=search)


@contacts_bp.route('/add', methods=['POST'])
@login_required
@whatsapp_setup_required
def add_contact():
    """Add a single contact"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    name = sanitize_input(request.form.get('name', ''))
    phone = sanitize_input(request.form.get('phone', ''))
    
    contact_service = get_contact_service()
    result = contact_service.add_contact(user.id, name, phone)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['error'], 'error')
    
    return redirect(url_for('main.dashboard'))


@contacts_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@whatsapp_setup_required
def upload_contacts():
    """Upload contacts page and handler"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        return _handle_csv_upload(user.id)
    
    # GET request - show upload page
    contact_service = get_contact_service()
    stats = contact_service.get_contact_stats(user.id)
    return render_template('upload_contacts.html', user=user, stats=stats)


@contacts_bp.route('/import', methods=['GET', 'POST'])
@login_required
@whatsapp_setup_required 
def import_contacts():
    """Import contacts (alias for upload)"""
    return redirect(url_for('contacts.upload_contacts'))


@contacts_bp.route('/download-sample')
@login_required
def download_sample_csv():
    """Download sample CSV file"""
    from flask import send_from_directory
    import os
    
    # Look for sample file in project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sample_file = os.path.join(project_root, 'sample_contacts_with_names.csv')
    
    if os.path.exists(sample_file):
        return send_from_directory(project_root, 'sample_contacts_with_names.csv', as_attachment=True)
    else:
        # Create a simple sample CSV on the fly
        from flask import Response
        sample_csv = "name,phone\nJohn Doe,1234567890\nJane Smith,0987654321\n"
        return Response(
            sample_csv,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=sample_contacts.csv"}
        )


def _handle_csv_upload(user_id: int):
    """Handle CSV file upload"""
    if 'csv_file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('contacts.upload_contacts'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('contacts.upload_contacts'))
    
    if not validate_csv_file(file.filename):
        flash('Please upload a valid CSV file', 'error')
        return redirect(url_for('contacts.upload_contacts'))
    
    try:
        # Read and sanitize CSV content
        content = file.read().decode('utf-8-sig')  # Handle BOM
        content = sanitize_csv_content(content)
        
        # Import contacts
        contact_service = get_contact_service()
        result = contact_service.import_from_csv(user_id, content)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['error'], 'error')
            
    except Exception as e:
        flash(f'Error importing CSV: {str(e)}', 'error')
    
    return redirect(url_for('contacts.upload_contacts'))
