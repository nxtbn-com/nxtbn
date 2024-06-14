import os
from django.conf import settings

def make_path(module_path):
    return os.path.join(*module_path.split('.')) + '/'
    