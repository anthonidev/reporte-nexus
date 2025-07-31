"""
Configuraciones y constantes para el análisis de membresías
"""

import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de rutas
DEFAULT_DATA_PATH = "data/membership/"
DEFAULT_OUTPUT_PATH = "reporte_membresias_completo.pdf"

# Configuración de meses
MONTHS = ['mayo', 'junio', 'julio']
MONTH_NAMES = {
    'mayo': 'Mayo',
    'junio': 'Junio',
    'julio': 'Julio'
}

# Configuración de estilos visuales
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Colores para gráficos
COLORS = {
    'primary': ['#FF6B6B', '#4ECDC4', '#45B7D1'],
    'secondary': ['#96CEB4', '#FECA57', '#FF9FF3'],
    'plans': ['#FF6B6B', '#4ECDC4', '#45B7D1'],
    'growth_positive': 'green',
    'growth_negative': 'red'
}

# Configuración de figura
FIGURE_SIZE = (11.7, 8.3)  # A4 landscape
FONT_SIZES = {
    'title': 18,
    'subtitle': 14,
    'normal': 12,
    'small': 10,
    'tiny': 9
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
    'analysis_start': "Iniciando analisis de membresias...",
    'analysis_complete': "Analisis completado!"
}

# Títulos de secciones del reporte
REPORT_TITLES = {
    'executive_summary': 'REPORTE DE MEMBRESÍAS - RESUMEN EJECUTIVO\nMayo - Julio 2024',
    'monthly_comparison': 'ANÁLISIS COMPARATIVO MENSUAL',
    'plan_analysis': 'ANÁLISIS POR PLANES DE MEMBRESÍA',
    'growth_overview': 'ANALISIS DE CRECIMIENTO - VISTA GENERAL',
    'monthly_growth': 'ANALISIS DE CRECIMIENTO - DETALLE MENSUAL',
    'plan_growth': 'ANALISIS DE CRECIMIENTO - POR PLANES',
    'detailed_data': 'DATOS DETALLADOS POR MES'
}
