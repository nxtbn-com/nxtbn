import os
import re
from django.conf import settings

def check_plugin_directory(payment_plugin_id):
    """Check if the directory for the given plugin exists."""
    plugin_path = os.path.join(settings.BASE_DIR, 'nxtbn', 'payment', 'plugins', payment_plugin_id)
    return os.path.exists(plugin_path)


def is_secure_path_name(path_name):
    """Validate the path name to prevent path injection attacks."""
    # Check if the path name contains more than one dot character
    if path_name.count('.') > 1:
        return False
    
    # Check if the path name contains directory separators
    if '/' in path_name or '\\' in path_name:
        return False
    
    # Check for problematic sequences such as "../"
    if '/../' in path_name or '\\..' in path_name:
        return False
    
    # Optionally, use an allowlist of known good patterns
    # For example, allow alphanumeric characters, underscores, and hyphens
    # Modify this pattern according to your requirements
    allowed_pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(allowed_pattern, path_name):
        return False
    
    # If all checks pass, the path name is valid
    return True


def security_validation(path_name): # Do we need this?
    """Perform security validation on the provided path name."""
    if not is_secure_path_name(path_name):
        raise ValueError("Invalid path name: {}".format(path_name))
