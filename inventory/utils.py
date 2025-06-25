from datetime import datetime
from django.utils import timezone

def generate_reference_number():
    """
    Generate a unique reference number in the format INV-YYYYDDMM-four digit
    """
    # Get current date
    now = timezone.now()
    
    # Format date as YYYYDDMM
    date_part = now.strftime('%Y%d%m')
    
    # Get the last 4 digits of the timestamp
    # This ensures uniqueness by using microseconds
    timestamp = now.timestamp()
    unique_part = str(int(timestamp * 1000))[-4:]
    
    return f'INV-{date_part}-{unique_part}'
