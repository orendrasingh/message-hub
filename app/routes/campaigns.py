"""
Campaign management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from app.models import DatabaseManager
from app.services.auth import AuthService
from app.services.whatsapp import WhatsAppService
from app.services.contact import ContactService
from app.services.campaign import CampaignService
from app.utils.auth import login_required, get_current_user, whatsapp_setup_required
from app.utils.validators import validate_message_template, sanitize_input
from app.utils.media import save_media_file, save_multiple_media_files, convert_to_base64_only, convert_multiple_files_to_base64, delete_media_file, get_media_type

campaigns_bp = Blueprint('campaigns', __name__)

# Get limiter instance
limiter = Limiter(key_func=get_remote_address)


def get_services():
    """Get service instances"""
    db_manager = DatabaseManager(current_app.config['DB_PATH'])
    auth_service = AuthService(
        db_manager,
        current_app.config['EVOLUTION_API_URL'],
        current_app.config['EVOLUTION_GLOBAL_KEY']
    )
    whatsapp_service = WhatsAppService(
        current_app.config['EVOLUTION_API_URL'],
        current_app.config['EVOLUTION_GLOBAL_KEY']
    )
    contact_service = ContactService(db_manager)
    campaign_service = CampaignService(db_manager, whatsapp_service)
    
    return auth_service, whatsapp_service, contact_service, campaign_service


@campaigns_bp.route('/send-single', methods=['GET', 'POST'])
@limiter.limit("100 per hour")
@login_required
@whatsapp_setup_required
def send_single():
    """Send single message with optional media"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        phone = sanitize_input(request.form.get('phone_number', ''))
        message = sanitize_input(request.form.get('message', ''))
        
        # Handle multiple media uploads
        media_files = request.files.getlist('media_files')
        media_data = None
        media_result = None
        
        if not phone:
            flash('Please provide a phone number', 'error')
        elif not message and not any(f.filename for f in media_files):
            flash('Please provide either a message or media files', 'error')
        else:
            try:
                # Process media files if provided
                if media_files and any(f.filename for f in media_files):
                    # Filter out empty files
                    valid_files = [f for f in media_files if f.filename]
                    
                    if valid_files:
                        media_result = save_multiple_media_files(valid_files)
                        if not media_result['success']:
                            flash(f'Media upload failed: {media_result.get("error", "Unknown error")}', 'error')
                            if 'errors' in media_result:
                                for error in media_result['errors']:
                                    flash(error, 'error')
                            return render_template('send_single.html')
                        
                        # Convert to base64 for Evolution API
                        file_paths = [f['file_path'] for f in media_result['files']]
                        media_data = convert_multiple_files_to_base64(file_paths)
                        
                        if not media_data:
                            flash('Failed to process media files', 'error')
                            # Clean up uploaded files
                            for file_info in media_result['files']:
                                delete_media_file(file_info['filename'])
                            return render_template('send_single.html')
                        
                        # Show warnings if any files failed
                        if 'warnings' in media_result:
                            for warning in media_result['warnings']:
                                flash(f'Warning: {warning}', 'warning')
                
                # Send message/media
                _, whatsapp_service, _, campaign_service = get_services()
                
                if media_data:
                    # Send multiple media files with caption
                    result = whatsapp_service.send_message_with_multiple_media(user, phone, message, media_data)
                else:
                    # Send text message only
                    result = whatsapp_service.send_message(user, phone, message)
                
                if result['success']:
                    # Log message with media info
                    log_message = message
                    if media_data:
                        log_message = f"[Media: {len(media_data)} files] {message}"
                    campaign_service._log_message(user.id, phone, log_message, 'sent')
                    flash('Message sent successfully!', 'success')
                    
                    # Clean up uploaded files after successful send
                    if media_data and media_result:
                        for file_info in media_result['files']:
                            delete_media_file(file_info['filename'])
                else:
                    flash(f'Failed to send message: {result["error"]}', 'error')
                    
                    # Clean up uploaded files on failure
                    if media_data and media_result:
                        for file_info in media_result['files']:
                            delete_media_file(file_info['filename'])
                    
            except Exception as e:
                flash(f'Error processing request: {str(e)}', 'error')
                # Clean up uploaded files on error
                if media_data and media_result:
                    for file_info in media_result['files']:
                        delete_media_file(file_info['filename'])
    
    # Get contacts and connection status
    _, whatsapp_service, contact_service, _ = get_services()
    contacts_data = contact_service.get_contacts(user.id, per_page=1000)  # Get all for dropdown
    connection_status = whatsapp_service.check_connection_status(user)
    
    return render_template('send_single.html',
                         contacts=contacts_data['contacts'],
                         user=user,
                         connection=connection_status)


@campaigns_bp.route('/bulk', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
@login_required
@whatsapp_setup_required
def bulk_campaign():
    """Bulk campaign page with media support"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        recipient_type = request.form.get('recipient_type', 'all')
        message = sanitize_input(request.form.get('message', ''))
        delay = int(request.form.get('delay', 5))
        
        # Handle multiple media files
        media_files = request.files.getlist('media_files')
        media_data = None
        
        # Process media files if provided
        if media_files and any(f.filename for f in media_files):
            # Filter out empty files
            valid_files = [f for f in media_files if f.filename]
            
            if valid_files:
                media_result = save_multiple_media_files(valid_files)
                if not media_result['success']:
                    flash(f'Media upload failed: {media_result.get("error", "Unknown error")}', 'error')
                    if 'errors' in media_result:
                        for error in media_result['errors']:
                            flash(error, 'error')
                    return _render_bulk_campaign_page(user)
                
                # Convert to base64 for WhatsApp API
                file_paths = [f['file_path'] for f in media_result['files']]
                media_data = convert_multiple_files_to_base64(file_paths)
                
                if not media_data:
                    flash('Failed to process media files', 'error')
                    # Clean up uploaded files
                    for file_info in media_result['files']:
                        delete_media_file(file_info['filename'])
                    return _render_bulk_campaign_page(user)
                
                # Show warnings if any files failed
                if 'warnings' in media_result:
                    for warning in media_result['warnings']:
                        flash(f'Warning: {warning}', 'warning')
        
        # Validate that we have either message or media
        if not message and not media_data:
            flash('Please provide either a message or media files', 'error')
            return _render_bulk_campaign_page(user)
        
        # Validate message if provided
        if message:
            message_validation = validate_message_template(message)
            if not message_validation['valid']:
                for error in message_validation['errors']:
                    flash(error, 'error')
                return _render_bulk_campaign_page(user)
        
        # Get contacts based on recipient type
        _, _, contact_service, campaign_service = get_services()
        
        if recipient_type == 'selected':
            selected_contacts = request.form.getlist('selected_contacts')
            if not selected_contacts:
                flash('Please select at least one contact', 'error')
                return _render_bulk_campaign_page(user)
            contacts = contact_service.get_contacts_for_campaign(user.id, recipient_type, selected_contacts)
        else:
            contacts = contact_service.get_contacts_for_campaign(user.id, recipient_type)
        
        if not contacts:
            flash('No contacts found to send messages to', 'error')
            return _render_bulk_campaign_page(user)
        
        # Start campaign with media support
        result = campaign_service.start_campaign_with_media(user.id, contacts, message, delay, media_data)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('campaigns.status'))
        else:
            flash(result['error'], 'error')
    
    return _render_bulk_campaign_page(user)


@campaigns_bp.route('/status')
@login_required
@whatsapp_setup_required
def status():
    """Campaign status page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    # Get services
    _, whatsapp_service, contact_service, campaign_service = get_services()
    
    # Get page data
    contacts_data = contact_service.get_contacts(user.id, per_page=5)
    connection_status = whatsapp_service.check_connection_status(user)
    stats = contact_service.get_contact_stats(user.id)
    
    return render_template('campaign_status.html',
                         contacts=contacts_data['contacts'],
                         user=user,
                         connection=connection_status,
                         stats=stats)


# Legacy route redirects
@campaigns_bp.route('/bulk_send', methods=['GET', 'POST'])
@login_required
def bulk_send():
    """Legacy bulk send route"""
    return redirect(url_for('campaigns.bulk_campaign'))


@campaigns_bp.route('/bulk_campaign', methods=['GET', 'POST'])
@login_required  
def bulk_campaign_legacy():
    """Legacy bulk campaign route"""
    return redirect(url_for('campaigns.bulk_campaign'))


@campaigns_bp.route('/campaign_status')
@login_required
def campaign_status():
    """Legacy campaign status route"""
    return redirect(url_for('campaigns.status'))


def _render_bulk_campaign_page(user):
    """Helper to render bulk campaign page with data"""
    _, whatsapp_service, contact_service, _ = get_services()
    
    contacts_data = contact_service.get_contacts(user.id, per_page=1000)  # Get all for selection
    connection_status = whatsapp_service.check_connection_status(user)
    stats = contact_service.get_contact_stats(user.id)
    
    return render_template('bulk_send_new.html',
                         contacts=contacts_data['contacts'],
                         user=user,
                         connection=connection_status,
                         stats=stats)
