"""Default settings for Richie's LTI consumer plugin."""
from django.conf import settings

LTI_CONSUMER_CONFIGURATION = getattr(settings, "LTI_CONSUMER_CONFIGURATION", [])
