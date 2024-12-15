# webconf/jinja2_env.py
import os
from jinja2 import Environment, FileSystemLoader
from django.conf import settings

def environment(**options):
    template_dir = os.path.join(settings.BASE_DIR, 'configurator', 'templates')
    env = Environment(
        loader=FileSystemLoader(loader=FileSystemLoader(template_dir)),
    )
    return env

