# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 13:58:56 2025

@author: jvz16
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "personal_shoppers.settings")

application = get_wsgi_application()
