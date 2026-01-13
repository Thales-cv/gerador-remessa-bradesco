import re
from typing import Tuple
from unidecode import unidecode
from datetime import datetime

def clean_non_digits(value: str) -> str:
    """Removes non-digit characters."""
    if not value:
        return ""
    return re.sub(r'\D', '', str(value))

def sanitize_text(text: str, allow_email=False) -> str:
    """
    Remove accents, special chars.
    If allow_email is False, keep only A-Z, 0-9, Space.
    If True, allow @ and . and - and _
    """
    if not text: 
        return ""
    
    # 1. Unidecode (Avó -> Avo)
    text = unidecode(str(text))
    # 2. Upper
    text = text.upper()
    
    if allow_email:
        # Allow A-Z, 0-9, space, @, ., -, _
        text = re.sub(r'[^A-Z0-9 @\.\-\_]', '', text)
    else:
        # Strict: A-Z, 0-9, Space
        text = re.sub(r'[^A-Z0-9 ]', '', text)
        
    return text.strip()

def validate_date_not_past(date_str: str) -> bool:
    """Input DD/MM/AAAA. Checks if >= today."""
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return dt >= today
    except:
        return False

def determine_inscription_type(value: str) -> Tuple[str, str]:
    """Returns ('1', cleaned_cpf) or ('2', cleaned_cnpj) or raises ValueError."""
    cleaned = clean_non_digits(value)
    
    # Auto-pad logic for potential lost leading zeros
    if len(cleaned) == 10: cleaned = "0" + cleaned
    if len(cleaned) == 13: cleaned = "0" + cleaned
            
    if len(cleaned) == 11:
        return '1', cleaned
    elif len(cleaned) == 14:
        return '2', cleaned
    else:
        return '0', cleaned

def format_value(value) -> str:
    """Formats float to string with 2 decimal places, no dots."""
    try:
        val_float = float(value)
        if val_float < 0: return "000" # Safety
        return "{:.2f}".format(val_float).replace('.', '')
    except:
        return "000"
