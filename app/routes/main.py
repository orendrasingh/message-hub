"""
Main application routes
"""

from flask import Blueprint, render_template, redirect, url_for, session, jsonify, current_app

from app.models import DatabaseManager
from app.services.auth import AuthService
from app.services.whatsapp import WhatsAppService
from app.services.contact import ContactService
from app.services.campaign import CampaignService
from app.utils.auth import login_required, get_current_user, anonymous_required

main_bp = Blueprint('main', __name__)


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


@main_bp.route('/')
@anonymous_required
def index():
    """Landing page"""
    return render_template('login.html')


@main_bp.route('/home')
@anonymous_required
def home():
    """Home page"""
    return render_template('login.html')


@main_bp.route('/landing')
def landing():
    """Public landing page"""
    return render_template('landing.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    # Check setup status
    if not user.instance_created:
        return redirect(url_for('main.setup_whatsapp'))
    elif not user.whatsapp_connected:
        return redirect(url_for('main.connect_whatsapp'))
    
    # Get services
    _, whatsapp_service, contact_service, campaign_service = get_services()
    
    # Get dashboard data
    contacts_data = contact_service.get_contacts(user.id, per_page=5)
    contact_stats = contact_service.get_contact_stats(user.id)
    connection_status = whatsapp_service.check_connection_status(user)
    recent_messages = campaign_service.get_recent_messages(user.id, limit=5)
    campaign_progress = campaign_service.get_campaign_progress(user.id)
    
    # Prepare stats
    stats = {
        'total_contacts': contact_stats['total'],
        'contacts_this_week': contact_stats.get('contacts_this_week', 0),
        'total_messages': contact_stats['total_messages'],
        'messages_today': contact_stats['messages_today'],
        'active_campaigns': 1 if campaign_progress['status'] == 'running' else 0,
        'active_campaign': campaign_progress if campaign_progress['status'] == 'running' else None
    }
    
    return render_template('dashboard.html',
                         user=user,
                         contacts=contacts_data['contacts'],
                         connection=connection_status,
                         stats=stats,
                         recent_messages=recent_messages)


@main_bp.route('/setup-whatsapp')
@login_required
def setup_whatsapp():
    """WhatsApp setup page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    if user.instance_created:
        return redirect(url_for('main.connect_whatsapp'))
    
    return render_template('setup_whatsapp.html', user=user)


@main_bp.route('/connect-whatsapp')
@login_required
def connect_whatsapp():
    """WhatsApp connection page"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    if not user.instance_created:
        return redirect(url_for('main.setup_whatsapp'))
    
    # Get QR code
    _, whatsapp_service, _, _ = get_services()
    qr_result = whatsapp_service.get_qr_code(user)
    
    return render_template('connect_whatsapp.html',
                         user=user,
                         qr_code=qr_result.get('qr_code', ''),
                         qr_error=qr_result.get('error', ''))


# Legacy route redirects for backward compatibility
@main_bp.route('/connect')
@login_required
def connect():
    """Legacy connect route"""
    return redirect(url_for('main.connect_whatsapp'))


@main_bp.route('/setup')
@login_required
def setup():
    """Legacy setup route"""
    return redirect(url_for('main.setup_whatsapp'))
