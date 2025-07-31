
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from .config import (
    FIGURE_SIZE, REPORT_TITLES, MESSAGES,
    FONT_SIZES, DEFAULT_OUTPUT_PATH
)
from .visualizations import MembershipVisualizations


class ReportGenerator:

    def __init__(self, combined_df, monthly_summary, stats):
        self.combined_df = combined_df
        self.monthly_summary = monthly_summary
        self.stats = stats
        self.visualizations = MembershipVisualizations(
            combined_df, monthly_summary, stats)

    def generate_pdf_report(self, output_file=DEFAULT_OUTPUT_PATH):
        """Genera el reporte PDF completo"""
        print(MESSAGES['pdf_generating'])

        with PdfPages(output_file) as pdf:
            self._create_executive_summary_page(pdf)

            self._create_monthly_comparison_page(pdf)

            self._create_plan_analysis_page(pdf)

            self._create_growth_overview_page(pdf)

            self._create_monthly_growth_page(pdf)

            self._create_plan_growth_page(pdf)

            self._create_detailed_tables_page(pdf)

        print(MESSAGES['pdf_success'].format(output_file=output_file))

    def _create_executive_summary_page(self, pdf):
        """Crea la página de resumen ejecutivo"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['executive_summary'],
                     fontsize=20, fontweight='bold', y=0.95)

        # Crear texto de resumen usando analytics
        summary_text = f"""
            METRICAS CLAVE DEL PERIODO:

            INGRESOS TOTALES: S/ {self.stats['total_revenue']:,.2f}
            TOTAL DE MEMBRESIAS: {self.stats['total_memberships']}
            CLIENTES UNICOS: {self.stats['unique_customers']}
            TICKET PROMEDIO: S/ {self.stats['avg_ticket']:,.2f}

            PLANES MAS EXITOSOS:
            {self.stats['by_plan'].head(3).to_string()}

            CRECIMIENTO MENSUAL:
            - Mayo a Junio: {self.stats['growth_rates']['ingresos']['Junio']:.1f}%
            - Junio a Julio: {self.stats['growth_rates']['ingresos']['Julio']:.1f}%

            PROYECCION AGOSTO:
            - Ingresos estimados: S/ {self.stats['projections']['agosto_ingresos_estimados']:,.0f}
            - Tendencia: {self.stats['projections']['tendencia_ingresos']}
        """

        plt.text(0.05, 0.85, summary_text, fontsize=FONT_SIZES['normal'],
                 fontfamily='serif', verticalalignment='top',
                 transform=fig.transFigure,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.5))

        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_monthly_comparison_page(self, pdf):
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['monthly_comparison'],
                     fontsize=FONT_SIZES['title'], fontweight='bold')

        self.visualizations.create_monthly_comparison_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_plan_analysis_page(self, pdf):
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['plan_analysis'],
                     fontsize=FONT_SIZES['title'], fontweight='bold')

        self.visualizations.create_plan_analysis_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_growth_overview_page(self, pdf):
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['growth_overview'],
                     fontsize=FONT_SIZES['title'], fontweight='bold')

        self.visualizations.create_growth_overview_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_monthly_growth_page(self, pdf):
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['monthly_growth'],
                     fontsize=FONT_SIZES['title'], fontweight='bold')

        self.visualizations.create_monthly_growth_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_plan_growth_page(self, pdf):
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['plan_growth'],
                     fontsize=FONT_SIZES['title'], fontweight='bold')

        self.visualizations.create_plan_growth_page(fig)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_detailed_tables_page(self, pdf):
        fig = plt.figure(figsize=FIGURE_SIZE)
        fig.suptitle(REPORT_TITLES['detailed_data'],
                     fontsize=FONT_SIZES['title'], fontweight='bold')

        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')

        table_data = self.monthly_summary.copy()
        table_data['ingresos_total'] = table_data['ingresos_total'].apply(
            lambda x: f'S/ {x:,.0f}')
        table_data['ticket_promedio'] = table_data['ticket_promedio'].apply(
            lambda x: f'S/ {x:,.0f}')

        table = ax.table(
            cellText=table_data.values,
            colLabels=['Mes', 'Orden', 'Ingresos Totales', 'Ticket Promedio',
                       'Total Membresías', 'Clientes Únicos'],
            cellLoc='center',
            loc='center',
            bbox=[0.1, 0.3, 0.8, 0.4]
        )

        table.auto_set_font_size(False)
        table.set_fontsize(FONT_SIZES['tiny'])
        table.scale(1, 2)

        plan_table_data = self.stats['by_plan'].copy()
        plan_table_data['ingresos'] = plan_table_data['ingresos'].apply(
            lambda x: f'S/ {x:,.0f}')
        plan_table_data['ticket_promedio'] = plan_table_data['ticket_promedio'].apply(
            lambda x: f'S/ {x:,.0f}')

        table2 = ax.table(
            cellText=plan_table_data.values,
            colLabels=['Ingresos', 'Cantidad',
                       'Ticket Promedio', 'Clientes Únicos'],
            rowLabels=plan_table_data.index,
            cellLoc='center',
            loc='center',
            bbox=[0.1, 0.05, 0.8, 0.2]
        )

        table2.auto_set_font_size(False)
        table2.set_fontsize(FONT_SIZES['tiny'])
        table2.scale(1, 1.5)

        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def generate_summary_report(self):
        summary = {
            'period': 'Mayo - Julio 2024',
            'total_revenue': self.stats['total_revenue'],
            'total_memberships': self.stats['total_memberships'],
            'unique_customers': self.stats['unique_customers'],
            'avg_ticket': self.stats['avg_ticket'],
            'best_month': self.stats['trends']['mejor_mes_ingresos'],
            'worst_month': self.stats['trends']['peor_mes_ingresos'],
            'best_plan': self.stats['by_plan'].index[0],
            'growth_trend': self.stats['projections']['tendencia_ingresos'],
            'august_projection': self.stats['projections']['agosto_ingresos_estimados']
        }

        return summary

    def export_data_to_excel(self, output_file="datos_membresias_detallados.xlsx"):
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Datos combinados
            self.combined_df.to_excel(
                writer, sheet_name='Datos_Completos', index=False)

            # Resumen mensual
            self.monthly_summary.to_excel(
                writer, sheet_name='Resumen_Mensual', index=False)

            # Estadísticas por plan
            self.stats['by_plan'].to_excel(
                writer, sheet_name='Estadisticas_Planes')

            # Tasas de crecimiento
            growth_df = pd.DataFrame(self.stats['growth_rates'])
            growth_df.to_excel(writer, sheet_name='Tasas_Crecimiento')

            # Cambios absolutos
            changes_df = pd.DataFrame(self.stats['absolute_changes'])
            changes_df.to_excel(writer, sheet_name='Cambios_Absolutos')

        print(f"Datos exportados a Excel: {output_file}")

    def validate_report_generation(self):
        issues = []

        # Verificar datos básicos
        if self.combined_df is None or self.combined_df.empty:
            issues.append("No hay datos combinados disponibles")

        if self.monthly_summary is None or self.monthly_summary.empty:
            issues.append("No hay resumen mensual disponible")

        if not self.stats:
            issues.append("No hay estadísticas calculadas")

        # Verificar estadísticas específicas
        required_stats = ['total_revenue',
                          'by_plan', 'growth_rates', 'projections']
        missing_stats = [
            stat for stat in required_stats if stat not in self.stats]
        if missing_stats:
            issues.append(f"Estadísticas faltantes: {missing_stats}")

        # Verificar que hay datos para los 3 meses
        if self.monthly_summary is not None:
            if len(self.monthly_summary) != 3:
                issues.append(
                    f"Solo hay {len(self.monthly_summary)} meses de datos")

        return issues
