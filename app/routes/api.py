"""
API routes for AJAX calls
"""

from flask import Blueprint, jsonify, request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.models import DatabaseManager
from app.services.auth import AuthService
from app.services.whatsapp import WhatsAppService
from app.services.contact import ContactService
from app.services.campaign import CampaignService
from app.utils.auth import login_required, get_current_user
from app.utils.validators import sanitize_input

api_bp = Blueprint('api', __name__)

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


# WhatsApp API endpoints
@api_bp.route('/qr-code')
@login_required
def get_qr_code():
    """Get fresh QR code"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    
    _, whatsapp_service, _, _ = get_services()
    result = whatsapp_service.get_qr_code(user)
    return jsonify(result)


@api_bp.route('/connection-status')
@login_required
def check_connection_status():
    """Check WhatsApp connection status"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    
    _, whatsapp_service, _, _ = get_services()
    result = whatsapp_service.check_connection_status(user)
    return jsonify(result)


# Legacy API endpoints for backward compatibility
@api_bp.route('/refresh-qr')
@login_required
def refresh_qr():
    """Legacy refresh QR endpoint"""
    return get_qr_code()


@api_bp.route('/check-connection')
@login_required
def check_connection():
    """Legacy check connection endpoint"""
    return check_connection_status()


# Contact management API endpoints
@api_bp.route('/contacts/edit', methods=['POST'])
@limiter.limit("60 per minute")
@login_required
def edit_contact():
    """Edit a contact"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    
    try:
        data = request.get_json()
        contact_id = data.get('id')
        name = sanitize_input(data.get('name', ''))
        phone = sanitize_input(data.get('phone', ''))
        
        _, _, contact_service, _ = get_services()
        result = contact_service.update_contact(contact_id, user.id, name, phone)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error'}), 500


@api_bp.route('/contacts/delete', methods=['POST'])
@limiter.limit("60 per minute")
@login_required
def delete_contact():
    """Delete a single contact"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    
    try:
        data = request.get_json()
        contact_id = data.get('id')
        
        _, _, contact_service, _ = get_services()
        result = contact_service.delete_contact(contact_id, user.id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error'}), 500


@api_bp.route('/contacts/delete-multiple', methods=['POST'])
@limiter.limit("30 per minute")
@login_required
def delete_contacts():
    """Delete multiple contacts"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    
    try:
        data = request.get_json()
        contact_ids = data.get('ids', [])
        
        _, _, contact_service, _ = get_services()
        result = contact_service.delete_contacts(contact_ids, user.id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error'}), 500


# Campaign API endpoints
@api_bp.route('/campaign/progress')
@login_required
def campaign_progress():
    """Get campaign progress"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    
    _, _, _, campaign_service = get_services()
    progress = campaign_service.get_campaign_progress(user.id)
    return jsonify(progress)


@api_bp.route('/campaign/stop', methods=['POST'])
@limiter.limit("10 per minute")
@login_required
def stop_campaign():
    """Stop active campaign"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    
    try:
        _, _, _, campaign_service = get_services()
        result = campaign_service.stop_campaign(user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': 'Server error'}), 500


@api_bp.route('/send-message', methods=['POST'])
@limiter.limit("100 per hour")
@login_required
def send_message():
    """Send single message via API"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    
    phone = sanitize_input(request.form.get('phone', ''))
    message = sanitize_input(request.form.get('message', ''))
    
    if not phone or not message:
        return jsonify({'success': False, 'error': 'Phone and message are required'})
    
    try:
        _, whatsapp_service, _, campaign_service = get_services()
        result = whatsapp_service.send_message(user, phone, message)
        
        if result['success']:
            # Log message
            campaign_service._log_message(user.id, phone, message, 'sent')
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


# Dashboard API endpoints
@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 401
    
    try:
        _, _, contact_service, _ = get_services()
        stats = contact_service.get_contact_stats(user.id)
        
        return jsonify({
            'total_contacts': stats['total'],
            'today_sent': stats['messages_today'],
            'total_sent': stats['total_messages']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Legacy API endpoints for backward compatibility
@api_bp.route('/edit-contact', methods=['POST'])
@login_required
def edit_contact_legacy():
    """Legacy edit contact endpoint"""
    return edit_contact()


@api_bp.route('/delete-contact', methods=['POST'])
@login_required
def delete_contact_legacy():
    """Legacy delete contact endpoint"""
    return delete_contact()


@api_bp.route('/delete-contacts', methods=['POST'])
@login_required
def delete_contacts_legacy():
    """Legacy delete contacts endpoint"""
    return delete_contacts()


@api_bp.route('/campaign_progress')
@login_required
def campaign_progress_legacy():
    """Legacy campaign progress endpoint"""
    return campaign_progress()


@api_bp.route('/stop-campaign', methods=['POST'])
@login_required
def stop_campaign_legacy():
    """Legacy stop campaign endpoint"""
    return stop_campaign()


@api_bp.route('/dashboard-stats')
@login_required
def dashboard_stats_legacy():
    """Legacy dashboard stats endpoint"""
    return dashboard_stats()
