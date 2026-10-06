"""Development settings for PharmaCare."""
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Disable strict password validation for easy development/testing
AUTH_PASSWORD_VALIDATORS = []
