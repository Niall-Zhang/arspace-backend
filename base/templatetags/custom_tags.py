# custom_tags/templatetags/custom_title_tags.py
from django import template
from utils.utils import get_settings

register = template.Library()

# Get setting meta_value by meta_key
@register.filter
def get_setting_meta_value_by_meta_key(meta_key):
    try:
        return get_settings(meta_key)
    except Exception as ex:
        return None