"""
Módulo para generar el reporte PDF completo de análisis total
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from .config import (
    FIGURE_SIZE, REPORT_TITLES, MESSAGES,
    FONT_SIZES, DEFAULT_OUTPUT_PATH
)
from .visualizations import TotalVisualizations


class TotalReportGenerator:
    """Maneja la generación del reporte PDF completo de análisis total"""

    def __init__(self, combined_df, monthly_summary, monthly_category_summary, stats):
        self.combined_df = combined_df
        self.monthly_summary = monthly_summary
        self.monthly_category_summary = monthly_category_summary
        self.stats = stats
        self.visualizations = TotalVisualizations(
            combined_df, monthly_summary, monthly_category_summary, stats
        )

    def generate_pdf_report(self, output_file=DEFAULT_OUTPUT_PATH):
        """Genera el reporte PDF completo"""
        print(MESSAGES['pdf_generating'])

        with PdfPages(output_file) as pdf:
            # Página 1: Resumen Ejecutivo
            self._create_executive_summary_page(pdf)

            # Página 2: Comparación Mensual
            self._create_monthly_comparison_page(pdf)

            # Página 3: Análisis por Categorías
            self._create_category_analysis_page(pdf)

            # Página 4: Crecimiento - Vista General
            self._create_growth_overview_page(pdf)

            # Página 5: Crecimiento - Detalle Mensual
            self._create_monthly_growth_page(pdf)

            # Página 6: Crecimiento - Por Categorías
            self._create_category_growth_page(pdf)

            # Página 7: Datos Detallados
            self._create_detailed_tables_page(pdf)

        print(MESSAGES['pdf_success'].format(output_file=output_file))

    def _create_executive_summary_page(self, pdf):
        """Crea la página de resumen ejecutivo"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['executive_summary'],
                     fontsize=FONT_SIZES['title'], fontweight='bold', y=0.95)

        self.visualizations.create_executive_summary_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_monthly_comparison_page(self, pdf):
        """Crea la página de comparación mensual"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['monthly_comparison'],
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')

        self.visualizations.create_monthly_comparison_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_category_analysis_page(self, pdf):
        """Crea la página de análisis por categorías"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['category_analysis'],
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')

        self.visualizations.create_category_analysis_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_growth_overview_page(self, pdf):
        """Crea la página de vista general de crecimiento"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['growth_overview'],
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')

        self.visualizations.create_growth_overview_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_monthly_growth_page(self, pdf):
        """Crea la página de crecimiento mensual detallado"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['monthly_growth'],
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')

        self.visualizations.create_monthly_growth_detail_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_category_growth_page(self, pdf):
        """Crea la página de crecimiento por categorías"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['category_growth'],
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')

        self.visualizations.create_category_growth_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_detailed_tables_page(self, pdf):
        """Crea la página con tablas detalladas"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['detailed_data'],
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')

        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')

        # Tabla 1: Resumen mensual
        table_data_monthly = self.monthly_summary.copy()
        table_data_monthly['ingresos_total'] = table_data_monthly['ingresos_total'].apply(
            lambda x: f'S/ {x:,.0f}')
        table_data_monthly['ticket_promedio'] = table_data_monthly['ticket_promedio'].apply(
            lambda x: f'S/ {x:,.0f}')

        table1 = ax.table(
            cellText=table_data_monthly.values,
            colLabels=['Mes', 'Orden', 'Ingresos Totales', 'Ticket Promedio',
                       'Total Transacciones', 'Clientes Únicos'],
            cellLoc='center',
            loc='center',
            bbox=[0.05, 0.7, 0.9, 0.25]
        )

        table1.auto_set_font_size(False)
        table1.set_fontsize(FONT_SIZES['tiny'])
        table1.scale(1, 2)

        # Título para tabla mensual
        ax.text(0.5, 0.97, 'RESUMEN MENSUAL', ha='center', va='top',
                fontsize=FONT_SIZES['section'], fontweight='bold', transform=ax.transAxes)

        # Tabla 2: Resumen por categorías
        table_data_category = self.stats['by_category'].copy()
        table_data_category['ingresos'] = table_data_category['ingresos'].apply(
            lambda x: f'S/ {x:,.0f}')
        table_data_category['ticket_promedio'] = table_data_category['ticket_promedio'].apply(
            lambda x: f'S/ {x:,.0f}')

        table2 = ax.table(
            cellText=table_data_category.values,
            colLabels=['Ingresos', 'Cantidad', 'Ticket Promedio',
                       'Ticket Mediano', 'Clientes Únicos'],
            rowLabels=table_data_category.index,
            cellLoc='center',
            loc='center',
            bbox=[0.05, 0.35, 0.9, 0.25]
        )

        table2.auto_set_font_size(False)
        table2.set_fontsize(FONT_SIZES['tiny'])
        table2.scale(1, 1.8)

        # Título para tabla de categorías
        ax.text(0.5, 0.62, 'RESUMEN POR CATEGORIAS', ha='center', va='top',
                fontsize=FONT_SIZES['section'], fontweight='bold', transform=ax.transAxes)

        # Resumen de insights clave
        insights_text = self._generate_insights_text()

        ax.text(0.5, 0.3, insights_text, ha='center', va='top',
                fontsize=FONT_SIZES['normal'], fontweight='bold', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f8f5", alpha=0.9))

        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _generate_insights_text(self):
        """Genera el texto de insights clave"""
        best_category = self.stats['trends']['mejor_categoria']
        best_month = self.stats['trends']['mejor_mes_ingresos']
        best_category_revenue = self.stats['by_category'].loc[best_category, 'ingresos']
        best_month_revenue = self.monthly_summary[
            self.monthly_summary['month'] == best_month
        ]['ingresos_total'].iloc[0]

        insights_text = f"""
INSIGHTS CLAVE DEL ANALISIS:

• CATEGORIA MAS RENTABLE: {best_category} 
  (S/ {best_category_revenue:,.0f})

• MAYOR CRECIMIENTO: {self.stats['trends']['categoria_mas_crecimiento']}

• MEJOR MES: {best_month} 
  (S/ {best_month_revenue:,.0f})

• PROYECCION AGOSTO: S/ {self.stats['projections']['agosto_ingresos_estimados']:,.0f}
  ({self.stats['projections']['tendencia_ingresos']})

• DIVERSIFICACION: {self.stats['diversity']['concentration_level']}
        """

        return insights_text

    def generate_summary_report(self):
        """Genera un resumen textual del análisis"""
        executive_data = self.stats.get('executive_summary_data', {})

        summary = {
            'period': 'Mayo - Julio 2024',
            'total_revenue': self.stats['total_revenue'],
            'total_transactions': self.stats['total_transactions'],
            'unique_customers': self.stats['unique_customers'],
            'avg_ticket': self.stats['avg_ticket'],
            'best_month': self.stats['trends']['mejor_mes_ingresos'],
            'best_category': self.stats['trends']['mejor_categoria'],
            'growth_trend': self.stats['projections']['tendencia_ingresos'],
            'august_projection': self.stats['projections']['agosto_ingresos_estimados'],
            'business_diversity': self.stats['diversity']['concentration_level'],
            'category_breakdown': self.stats['by_category']['ingresos'].to_dict(),
            'monthly_breakdown': dict(zip(
                self.monthly_summary['month'],
                self.monthly_summary['ingresos_total']
            ))
        }

        return summary

    def export_data_to_excel(self, output_file="datos_totales_detallados.xlsx"):
        """Exporta todos los datos procesados a Excel"""
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Datos combinados
            self.combined_df.to_excel(
                writer, sheet_name='Datos_Completos', index=False)

            # Resumen mensual
            self.monthly_summary.to_excel(
                writer, sheet_name='Resumen_Mensual', index=False)

            # Resumen mensual por categoría
            self.monthly_category_summary.to_excel(
                writer, sheet_name='Resumen_Mensual_Categoria', index=False
            )

            # Estadísticas por categoría
            self.stats['by_category'].to_excel(
                writer, sheet_name='Estadisticas_Categorias')

            # Tasas de crecimiento
            growth_df = pd.DataFrame(self.stats['growth_rates'])
            growth_df.to_excel(writer, sheet_name='Tasas_Crecimiento')

            # Cambios absolutos
            changes_df = pd.DataFrame(self.stats['absolute_changes'])
            changes_df.to_excel(writer, sheet_name='Cambios_Absolutos')

            # Métricas de diversidad
            diversity_df = pd.DataFrame([self.stats['diversity']])
            diversity_df.to_excel(
                writer, sheet_name='Metricas_Diversidad', index=False)

            # Participación por categorías
            participation_df = pd.DataFrame({
                'Categoria': self.stats['category_participation'].index,
                'Participacion_Porcentual': self.stats['category_participation'].values
            })
            participation_df.to_excel(
                writer, sheet_name='Participacion_Categorias', index=False)

        print(f"Datos exportados a Excel: {output_file}")

    def generate_business_intelligence_summary(self):
        """Genera un resumen de inteligencia de negocios"""
        bi_summary = {
            'kpis': {
                'revenue_growth_rate': self.stats['trends']['promedio_crecimiento_ingresos'],
                'customer_acquisition': self.stats['unique_customers'],
                'average_order_value': self.stats['avg_ticket'],
                'transaction_volume': self.stats['total_transactions']
            },
            'trends': {
                'seasonality': self.stats['seasonality']['pattern'],
                'peak_month': self.stats['seasonality']['peak_month'],
                'growth_trajectory': self.stats['projections']['tendencia_ingresos']
            },
            'category_performance': {
                'leader': self.stats['trends']['mejor_categoria'],
                'fastest_growing': self.stats['trends']['categoria_mas_crecimiento'],
                'concentration_risk': self.stats['diversity']['concentration_level']
            },
            'projections': {
                'next_month_revenue': self.stats['projections']['agosto_ingresos_estimados'],
                'confidence_level': self.stats['projections']['confianza_proyeccion']
            },
            'anomalies': self.stats.get('anomalies', [])
        }

        return bi_summary

    def validate_report_generation(self):
        """Valida que todos los datos necesarios están disponibles para el reporte"""
        issues = []

        # Verificar datos básicos
        if self.combined_df is None or self.combined_df.empty:
            issues.append("No hay datos combinados disponibles")

        if self.monthly_summary is None or self.monthly_summary.empty:
            issues.append("No hay resumen mensual disponible")

        if self.monthly_category_summary is None or self.monthly_category_summary.empty:
            issues.append("No hay resumen mensual por categoría disponible")

        if not self.stats:
            issues.append("No hay estadísticas calculadas")

        # Verificar estadísticas específicas
        required_stats = [
            'total_revenue', 'by_category', 'growth_rates',
            'projections', 'trends', 'diversity'
        ]
        missing_stats = [
            stat for stat in required_stats if stat not in self.stats]
        if missing_stats:
            issues.append(f"Estadísticas faltantes: {missing_stats}")

        # Verificar que hay datos para los 3 meses
        if self.monthly_summary is not None:
            if len(self.monthly_summary) != 3:
                issues.append(
                    f"Solo hay {len(self.monthly_summary)} meses de datos")

        # Verificar integridad de categorías
        if 'by_category' in self.stats:
            if len(self.stats['by_category']) == 0:
                issues.append("No hay datos de categorías")

        return issues

    def create_dashboard_data(self):
        """Genera datos estructurados para un dashboard"""
        dashboard_data = {
            'summary_cards': {
                'total_revenue': {
                    'value': self.stats['total_revenue'],
                    'format': 'currency',
                    'trend': self.stats['projections']['tendencia_ingresos']
                },
                'total_transactions': {
                    'value': self.stats['total_transactions'],
                    'format': 'number',
                    'trend': self.stats['projections']['tendencia_transacciones']
                },
                'avg_ticket': {
                    'value': self.stats['avg_ticket'],
                    'format': 'currency',
                    'trend': 'stable'
                },
                'unique_customers': {
                    'value': self.stats['unique_customers'],
                    'format': 'number',
                    'trend': 'growing'
                }
            },
            'time_series': {
                'monthly_revenue': dict(zip(
                    self.monthly_summary['month'],
                    self.monthly_summary['ingresos_total']
                )),
                'monthly_transactions': dict(zip(
                    self.monthly_summary['month'],
                    self.monthly_summary['total_transacciones']
                ))
            },
            'category_breakdown': self.stats['by_category']['ingresos'].to_dict(),
            'growth_rates': {
                key: value.to_dict() for key, value in self.stats['growth_rates'].items()
            }
        }

        return dashboard_data
