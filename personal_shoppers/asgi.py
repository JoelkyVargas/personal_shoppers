# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:57:40 2025

@author: jvz16
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "personal_shoppers.settings")

application = get_asgi_application()
