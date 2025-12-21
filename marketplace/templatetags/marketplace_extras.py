# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 16:49:16 2025

@author: jvz16
"""

from django import template

register = template.Library()


@register.filter
def moneda(value):
    """
    Formatea un entero con puntos como separador de miles.
    1250000 -> '1.250.000'
    """
    try:
        value_int = int(value)
    except (TypeError, ValueError):
        return value
    s = f"{value_int:,.0f}"
    return s.replace(",", ".")
