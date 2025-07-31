"""
Configuraciones y constantes para el análisis total de pagos
"""

import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de rutas
DEFAULT_DATA_PATH = "data/total/"
DEFAULT_OUTPUT_PATH = "reporte_pagos_totales_completo.pdf"

# Configuración de meses
MONTHS = ['mayo', 'junio', 'julio']
MONTH_NAMES = {
    'mayo': 'Mayo',
    'junio': 'Junio',
    'julio': 'Julio'
}

# Configuración de categorías
CATEGORY_NAMES = {
    'membership': 'Membresías',
    'order': 'Productos',
    'membership_reconsumption': 'Reconsumo',
    'membership_upgrade': 'Upgrade'
}

# Configuración de estilos visuales
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Colores para gráficos
COLORS = {
    'primary': ['#FF6B6B', '#4ECDC4', '#45B7D1'],
    'secondary': ['#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF'],
    'categories': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
    'growth_positive': 'green',
    'growth_negative': 'red',
    'heatmap': 'YlOrRd'
}

# Configuración de figura
FIGURE_SIZE = (11.7, 8.3)  # A4 landscape
FONT_SIZES = {
    'title': 20,
    'subtitle': 16,
    'section': 14,
    'normal': 12,
    'small': 11,
    'tiny': 10,
    'mini': 9
}

# Configuración de grid
GRID_CONFIG = {
    'hspace': 0.3,
    'wspace': 0.3,
    'detailed_hspace': 0.4
}

# Mensajes y textos
MESSAGES = {
    'loading_success': "Cargado: {file_path} - {records} registros",
    'loading_error': "No se encontro: {file_path}",
    'pdf_generating': "Generando reporte PDF...",
    'pdf_success': "Reporte generado exitosamente: {output_file}",
    'analysis_start': "Iniciando analisis de pagos totales...",
    'analysis_complete': "Analisis completado!"
}

# Títulos de secciones del reporte
REPORT_TITLES = {
    'executive_summary': 'REPORTE TOTAL DE PAGOS - RESUMEN EJECUTIVO\nMayo - Julio 2024',
    'monthly_comparison': 'COMPARACION MENSUAL - TODAS LAS CATEGORIAS',
    'category_analysis': 'ANALISIS DETALLADO POR CATEGORIAS',
    'growth_overview': 'ANALISIS DE CRECIMIENTO - VISTA GENERAL',
    'monthly_growth': 'ANALISIS DE CRECIMIENTO - DETALLE MENSUAL',
    'category_growth': 'ANALISIS DE CRECIMIENTO - POR CATEGORIAS',
    'detailed_data': 'DATOS DETALLADOS - RESUMEN COMPLETO'
}

# Configuración para heatmaps
HEATMAP_CONFIG = {
    'cmap': 'YlOrRd',
    'aspect': 'auto',
    'text_color_threshold': 0.5,
    'text_colors': ['black', 'white']
}
