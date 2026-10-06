import uuid
from .models import AuditLog

def get_client_ip(request):
    """Safely extracts the client IP address from the request object."""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_audit_action(user, action, model_name, object_id, description, request=None):
    """
    Creates an immutable audit log entry.
    Never logs sensitive passwords, tokens, or payment details.
    """
    ip_address = get_client_ip(request) if request else None
    return AuditLog.objects.create(
        user=user if (user and user.is_authenticated) else None,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else '',
        description=description,
        ip_address=ip_address
    )

def generate_unique_code(prefix='ORD'):
    """Generates human-readable, unique identifiers for orders, tracking, and batches."""
    random_part = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{random_part}"
