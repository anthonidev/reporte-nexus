"""
Paquete de análisis total de pagos
Proporciona funcionalidades para analizar todos los tipos de pagos y generar reportes PDF
"""

from .data_loader import TotalDataLoader
from .analytics import TotalAnalytics
from .visualizations import TotalVisualizations
from .report_generator import TotalReportGenerator

__version__ = "1.0.0"
__author__ = "Tu Nombre"

__all__ = [
    'TotalDataLoader',
    'TotalAnalytics',
    'TotalVisualizations',
    'TotalReportGenerator'
]
