"""
Módulo para crear visualizaciones y gráficos para análisis total
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.total.config import COLORS, FONT_SIZES, GRID_CONFIG, HEATMAP_CONFIG


class TotalVisualizations:
    """Maneja la creación de todos los gráficos del reporte total"""

    def __init__(self, combined_df, monthly_summary, monthly_category_summary, stats):
        self.combined_df = combined_df
        self.monthly_summary = monthly_summary
        self.monthly_category_summary = monthly_category_summary
        self.stats = stats

    def create_executive_summary_page(self, fig):
        """Crea la página de resumen ejecutivo"""
        gs = fig.add_gridspec(
            2, 2, hspace=GRID_CONFIG['hspace'], wspace=GRID_CONFIG['wspace'])

        # 1. Gráfico de ingresos totales por mes
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_monthly_revenue_bars(ax1)

        # 2. Distribución por categorías (pie chart)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_category_distribution_pie(ax2)

        # 3. Resumen de métricas clave (texto)
        ax3 = fig.add_subplot(gs[1, :])
        self._create_executive_summary_text(ax3)

    def _plot_monthly_revenue_bars(self, ax):
        """Gráfico de barras de ingresos mensuales"""
        months = self.monthly_summary['month'].tolist()
        revenue = self.monthly_summary['ingresos_total'].tolist()

        bars = ax.bar(months, revenue, color=COLORS['primary'], alpha=0.8)
        ax.set_title('INGRESOS TOTALES POR MES',
                     fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.set_ylabel('Ingresos (S/)',
                      fontsize=FONT_SIZES['normal'], fontweight='bold')

        # Agregar valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'S/ {height:,.0f}', ha='center', va='bottom',
                    fontweight='bold', fontsize=FONT_SIZES['small'])

        ax.grid(True, alpha=0.3)

    def _plot_category_distribution_pie(self, ax):
        """Gráfico circular de distribución por categorías"""
        category_totals = self.stats['by_category']['ingresos']
        colors = COLORS['categories'][:len(category_totals)]

        wedges, texts, autotexts = ax.pie(
            category_totals.values,
            labels=category_totals.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        ax.set_title('DISTRIBUCION POR CATEGORIAS',
                     fontsize=FONT_SIZES['section'], fontweight='bold')

    def _create_executive_summary_text(self, ax):
        """Crea el texto del resumen ejecutivo"""
        ax.axis('off')

        # Calcular crecimiento total
        revenue = self.monthly_summary['ingresos_total'].tolist()
        total_growth_revenue = (
            (revenue[-1] - revenue[0]) / revenue[0]) * 100 if revenue[0] != 0 else 0

        summary_text = f"""
METRICAS CLAVE DEL PERIODO (Mayo - Julio):

INGRESOS TOTALES: S/ {self.stats['total_revenue']:,.2f}
TOTAL TRANSACCIONES: {self.stats['total_transactions']}
CLIENTES UNICOS: {self.stats['unique_customers']}
TICKET PROMEDIO: S/ {self.stats['avg_ticket']:,.2f}

CRECIMIENTO TOTAL: {total_growth_revenue:+.1f}%
MEJOR MES: {self.stats['trends']['mejor_mes_ingresos']}
CATEGORIA MAS EXITOSA: {self.stats['trends']['mejor_categoria']}

DISTRIBUCION POR CATEGORIA:
{self.stats['by_category'].to_string()}

PROYECCIONES AGOSTO:
• Ingresos estimados: S/ {self.stats['projections']['agosto_ingresos_estimados']:,.0f}
• Transacciones estimadas: {self.stats['projections']['agosto_transacciones_estimadas']:.0f}
        """

        ax.text(0.02, 0.98, summary_text, fontsize=FONT_SIZES['small'], fontweight='bold',
                verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f8ff", alpha=0.9))

    def create_monthly_comparison_page(self, fig):
        """Crea la página de comparación mensual"""
        gs = fig.add_gridspec(
            2, 2, hspace=GRID_CONFIG['detailed_hspace'], wspace=GRID_CONFIG['wspace'])

        # 1. Ingresos por mes
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_monthly_revenue_bars(ax1)

        # 2. Número de transacciones por mes
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_monthly_transactions(ax2)

        # 3. Ticket promedio por mes
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_monthly_tickets(ax3)

        # 4. Evolución de ingresos por categoría
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_category_evolution_lines(ax4)

        plt.tight_layout()

    def _plot_monthly_transactions(self, ax):
        """Gráfico de transacciones mensuales"""
        months = self.monthly_summary['month'].tolist()
        transactions = self.monthly_summary['total_transacciones'].tolist()

        bars = ax.bar(months, transactions, color=COLORS['primary'])
        ax.set_title('Transacciones por Mes',
                     fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.set_ylabel('Cantidad', fontsize=FONT_SIZES['normal'])

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')

    def _plot_monthly_tickets(self, ax):
        """Gráfico de ticket promedio mensual"""
        months = self.monthly_summary['month'].tolist()
        tickets = self.monthly_summary['ticket_promedio'].tolist()

        bars = ax.bar(months, tickets, color=COLORS['primary'])
        ax.set_title('Ticket Promedio por Mes',
                     fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.set_ylabel('Ticket Promedio (S/)', fontsize=FONT_SIZES['normal'])

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'S/ {height:,.0f}', ha='center', va='bottom', fontweight='bold')

    def _plot_category_evolution_lines(self, ax):
        """Gráfico de líneas de evolución por categoría"""
        category_evolution = self.combined_df.groupby(['month', 'category_clean'])[
            'amount'].sum().unstack(fill_value=0)
        colors = COLORS['categories']

        for i, category in enumerate(category_evolution.columns):
            ax.plot(category_evolution.index, category_evolution[category],
                    marker='o', linewidth=3, markersize=8, label=category, color=colors[i])

        ax.set_title('Evolución por Categoría',
                     fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.set_ylabel('Ingresos (S/)', fontsize=FONT_SIZES['normal'])
        ax.legend(fontsize=FONT_SIZES['tiny'], loc='upper left')
        ax.grid(True, alpha=0.3)

    def create_category_analysis_page(self, fig):
        """Crea la página de análisis por categorías"""
        gs = fig.add_gridspec(
            2, 3, hspace=GRID_CONFIG['detailed_hspace'], wspace=GRID_CONFIG['wspace'])

        # 1. Ingresos por categoría (horizontal bar)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_category_revenue_horizontal(ax1)

        # 2. Cantidad por categoría
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_category_count_horizontal(ax2)

        # 3. Ticket promedio por categoría
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_category_tickets_horizontal(ax3)

        # 4. Mapa de calor - categorías por mes
        ax4 = fig.add_subplot(gs[1, :])
        self._plot_category_month_heatmap(ax4)

    def _plot_category_revenue_horizontal(self, ax):
        """Gráfico horizontal de ingresos por categoría"""
        category_revenue = self.stats['by_category']['ingresos'].sort_values(
            ascending=True)
        colors = COLORS['secondary'][:len(category_revenue)]

        bars = ax.barh(category_revenue.index,
                       category_revenue.values, color=colors)
        ax.set_title('Ingresos por Categoría',
                     fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_xlabel('Ingresos (S/)', fontsize=FONT_SIZES['tiny'])

        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'S/ {width:,.0f}', ha='left', va='center',
                    fontweight='bold', fontsize=FONT_SIZES['mini'])

    def _plot_category_count_horizontal(self, ax):
        """Gráfico horizontal de cantidad por categoría"""
        category_count = self.stats['by_category']['cantidad'].sort_values(
            ascending=True)
        colors = COLORS['secondary'][:len(category_count)]

        bars = ax.barh(category_count.index,
                       category_count.values, color=colors)
        ax.set_title('Cantidad por Categoría',
                     fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_xlabel('Cantidad', fontsize=FONT_SIZES['tiny'])

        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}', ha='left', va='center',
                    fontweight='bold', fontsize=FONT_SIZES['mini'])

    def _plot_category_tickets_horizontal(self, ax):
        """Gráfico horizontal de ticket promedio por categoría"""
        category_ticket = self.stats['by_category']['ticket_promedio'].sort_values(
            ascending=True)
        colors = COLORS['secondary'][:len(category_ticket)]

        bars = ax.barh(category_ticket.index,
                       category_ticket.values, color=colors)
        ax.set_title('Ticket Promedio',
                     fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_xlabel('Ticket (S/)', fontsize=FONT_SIZES['tiny'])

        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'S/ {width:,.0f}', ha='left', va='center',
                    fontweight='bold', fontsize=FONT_SIZES['mini'])

    def _plot_category_month_heatmap(self, ax):
        """Mapa de calor de categorías por mes"""
        heatmap_data = self.combined_df.groupby(['month', 'category_clean'])[
            'amount'].sum().unstack(fill_value=0)

        im = ax.imshow(heatmap_data.T.values, cmap=HEATMAP_CONFIG['cmap'],
                       aspect=HEATMAP_CONFIG['aspect'])
        ax.set_xticks(range(len(heatmap_data.index)))
        ax.set_xticklabels(heatmap_data.index)
        ax.set_yticks(range(len(heatmap_data.columns)))
        ax.set_yticklabels(heatmap_data.columns)
        ax.set_title('MAPA DE CALOR - INGRESOS POR CATEGORIA Y MES',
                     fontsize=FONT_SIZES['section'], fontweight='bold', pad=20)

        # Agregar valores en el heatmap
        threshold = heatmap_data.values.max(
        ) * HEATMAP_CONFIG['text_color_threshold']
        for i in range(len(heatmap_data.columns)):
            for j in range(len(heatmap_data.index)):
                value = heatmap_data.iloc[j, i]
                text_color = HEATMAP_CONFIG['text_colors'][1] if value > threshold else HEATMAP_CONFIG['text_colors'][0]
                ax.text(j, i, f'S/ {value:,.0f}', ha='center', va='center',
                        fontweight='bold', fontsize=FONT_SIZES['tiny'], color=text_color)

        # Colorbar
        cbar = plt.colorbar(
            im, ax=ax, orientation='horizontal', pad=0.1, shrink=0.8)
        cbar.set_label('Ingresos (S/)', fontweight='bold')

    def create_growth_overview_page(self, fig):
        """Crea la página de vista general de crecimiento"""
        gs = fig.add_gridspec(
            2, 2, hspace=GRID_CONFIG['hspace'], wspace=GRID_CONFIG['wspace'])

        # 1. Evolución principal (gráfico más grande)
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_main_evolution_dual_axis(ax1)

        # 2. Resumen de crecimiento
        ax2 = fig.add_subplot(gs[1, 0])
        self._create_growth_summary_text(ax2)

        # 3. Proyecciones
        ax3 = fig.add_subplot(gs[1, 1])
        self._create_projections_text(ax3)

    def _plot_main_evolution_dual_axis(self, ax):
        """Gráfico principal de evolución con doble eje Y"""
        months = self.monthly_summary['month'].tolist()
        revenue = self.monthly_summary['ingresos_total'].tolist()
        transactions = self.monthly_summary['total_transacciones'].tolist()

        ax_twin = ax.twinx()

        # Línea de ingresos
        line1 = ax.plot(months, revenue, color='#FF6B6B', marker='o',
                        linewidth=4, markersize=12, label='Ingresos (S/)')
        ax.set_ylabel('Ingresos (S/)', color='#FF6B6B',
                      fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.tick_params(axis='y', labelcolor='#FF6B6B',
                       labelsize=FONT_SIZES['normal'])

        # Línea de transacciones
        line2 = ax_twin.plot(months, transactions, color='#4ECDC4', marker='s',
                             linewidth=4, markersize=12, label='Transacciones')
        ax_twin.set_ylabel('Número de Transacciones', color='#4ECDC4',
                           fontsize=FONT_SIZES['section'], fontweight='bold')
        ax_twin.tick_params(axis='y', labelcolor='#4ECDC4',
                            labelsize=FONT_SIZES['normal'])

        ax.set_title('EVOLUCION MENSUAL - INGRESOS Y TRANSACCIONES',
                     fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)

        # Agregar valores en los puntos
        for i, (month, rev, trans) in enumerate(zip(months, revenue, transactions)):
            ax.annotate(f'S/ {rev:,.0f}', (i, rev), textcoords="offset points",
                        xytext=(0, 20), ha='center', fontweight='bold',
                        color='#FF6B6B', fontsize=FONT_SIZES['normal'])
            ax_twin.annotate(f'{trans}', (i, trans), textcoords="offset points",
                             xytext=(0, -25), ha='center', fontweight='bold',
                             color='#4ECDC4', fontsize=FONT_SIZES['normal'])

    def _create_growth_summary_text(self, ax):
        """Crea el texto de resumen de crecimiento"""
        ax.axis('off')

        revenue = self.monthly_summary['ingresos_total'].tolist()
        transactions = self.monthly_summary['total_transacciones'].tolist()

        total_growth_revenue = (
            (revenue[-1] - revenue[0]) / revenue[0]) * 100 if revenue[0] != 0 else 0
        total_growth_transactions = (
            (transactions[-1] - transactions[0]) / transactions[0]) * 100 if transactions[0] != 0 else 0

        growth_text = f"""
CRECIMIENTO TOTAL (Mayo - Julio):

INGRESOS:
• Crecimiento: {total_growth_revenue:+.1f}%
• De S/ {revenue[0]:,.0f} a S/ {revenue[-1]:,.0f}

TRANSACCIONES:
• Crecimiento: {total_growth_transactions:+.1f}%
• De {transactions[0]} a {transactions[-1]}

MEJOR MES: {self.stats['trends']['mejor_mes_ingresos']}
CATEGORIA TOP: {self.stats['trends']['mejor_categoria']}
        """

        ax.text(0.05, 0.95, growth_text, fontsize=FONT_SIZES['normal'], fontweight='bold',
                verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f4fd", alpha=0.9))

    def _create_projections_text(self, ax):
        """Crea el texto de proyecciones"""
        ax.axis('off')

        projection_text = f"""
PROYECCIONES AGOSTO:

INGRESOS ESTIMADOS:
• S/ {self.stats['projections']['agosto_ingresos_estimados']:,.0f}
• Tendencia: {self.stats['projections']['tendencia_ingresos']}

TRANSACCIONES ESTIMADAS:
• {self.stats['projections']['agosto_transacciones_estimadas']:.0f}
• Tendencia: {self.stats['projections']['tendencia_transacciones']}

PROMEDIO CRECIMIENTO:
• {self.stats['trends']['promedio_crecimiento_ingresos']:.1f}% mensual
        """

        ax.text(0.05, 0.95, projection_text, fontsize=FONT_SIZES['normal'], fontweight='bold',
                verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff2e8", alpha=0.9))

    def create_monthly_growth_detail_page(self, fig):
        """Crea la página de detalle de crecimiento mensual"""
        gs = fig.add_gridspec(
            2, 2, hspace=GRID_CONFIG['detailed_hspace'], wspace=GRID_CONFIG['wspace'])

        # 1. Tasas de crecimiento porcentual
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_growth_rates_bars(ax1)

        # 2. Cambios absolutos
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_absolute_changes_bars(ax2)

        # 3. Evolución del ticket promedio
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_ticket_evolution_line(ax3)

        # 4. Panel de detalles
        ax4 = fig.add_subplot(gs[1, 1])
        self._create_monthly_details_text(ax4)

    def _plot_growth_rates_bars(self, ax):
        """Gráfico de tasas de crecimiento porcentual"""
        growth_data = {
            'Ingresos': [self.stats['growth_rates']['ingresos']['Junio'],
                         self.stats['growth_rates']['ingresos']['Julio']],
            'Transacciones': [self.stats['growth_rates']['transacciones']['Junio'],
                              self.stats['growth_rates']['transacciones']['Julio']]
        }

        x_pos = np.arange(len(['Jun vs May', 'Jul vs Jun']))
        width = 0.35

        bars1 = ax.bar(x_pos - width/2, growth_data['Ingresos'], width,
                       label='Ingresos', color='#FF6B6B', alpha=0.8)
        bars2 = ax.bar(x_pos + width/2, growth_data['Transacciones'], width,
                       label='Transacciones', color='#4ECDC4', alpha=0.8)

        ax.set_ylabel('Crecimiento (%)',
                      fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_title('TASAS DE CRECIMIENTO',
                     fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(['Jun vs May', 'Jul vs Jun'],
                           fontsize=FONT_SIZES['small'])
        ax.legend(fontsize=FONT_SIZES['small'])
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.grid(True, alpha=0.3)

        # Agregar valores
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3 if height >= 0 else -15),
                            textcoords="offset points",
                            ha='center', va='bottom' if height >= 0 else 'top',
                            fontweight='bold', fontsize=FONT_SIZES['tiny'])

    def _plot_absolute_changes_bars(self, ax):
        """Gráfico de cambios absolutos"""
        revenue_changes = [
            self.stats['absolute_changes']['ingresos']['Junio'],
            self.stats['absolute_changes']['ingresos']['Julio']
        ]
        colors = [COLORS['growth_positive'] if x >= 0 else COLORS['growth_negative']
                  for x in revenue_changes]

        bars = ax.bar(['Jun vs May', 'Jul vs Jun'], revenue_changes,
                      color=colors, alpha=0.7)
        ax.set_ylabel('Cambio Absoluto (S/)',
                      fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_title('CAMBIO EN INGRESOS',
                     fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax.grid(True, alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'S/ {height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -15),
                        textcoords="offset points",
                        ha='center', va='bottom' if height >= 0 else 'top',
                        fontweight='bold', fontsize=FONT_SIZES['tiny'])

    def _plot_ticket_evolution_line(self, ax):
        """Gráfico de evolución del ticket promedio"""
        months = self.monthly_summary['month'].tolist()
        tickets = self.monthly_summary['ticket_promedio'].tolist()

        ax.plot(months, tickets, color='#45B7D1', marker='D',
                linewidth=4, markersize=10)
        ax.set_ylabel('Ticket Promedio (S/)',
                      fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_title('EVOLUCION TICKET PROMEDIO',
                     fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.grid(True, alpha=0.3)

        for i, (month, ticket) in enumerate(zip(months, tickets)):
            ax.annotate(f'S/ {ticket:,.0f}', (i, ticket), textcoords="offset points",
                        xytext=(0, 15), ha='center', fontweight='bold',
                        fontsize=FONT_SIZES['small'])

    def _create_monthly_details_text(self, ax):
        """Crea el texto de detalles mensuales"""
        ax.axis('off')

        details_text = f"""
DETALLES MES A MES:

MAYO → JUNIO:
• Ingresos: {self.stats['growth_rates']['ingresos']['Junio']:+.1f}%
• Transacciones: {self.stats['growth_rates']['transacciones']['Junio']:+.1f}%
• Clientes: {self.stats['growth_rates']['clientes_unicos']['Junio']:+.1f}%

JUNIO → JULIO:
• Ingresos: {self.stats['growth_rates']['ingresos']['Julio']:+.1f}%
• Transacciones: {self.stats['growth_rates']['transacciones']['Julio']:+.1f}%
• Clientes: {self.stats['growth_rates']['clientes_unicos']['Julio']:+.1f}%
        """

        ax.text(0.05, 0.95, details_text, fontsize=FONT_SIZES['small'], fontweight='bold',
                verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f8e8", alpha=0.9))

    def create_category_growth_page(self, fig):
        """Crea la página de crecimiento por categorías"""
        gs = fig.add_gridspec(
            3, 2, hspace=GRID_CONFIG['detailed_hspace'], wspace=GRID_CONFIG['wspace'])

        # 1. Crecimiento de ingresos por categoría
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_category_revenue_growth_bars(ax1)

        # 2. Crecimiento de cantidad por categoría
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_category_count_growth_bars(ax2)

        # 3. Evolución temporal completa por categoría
        ax3 = fig.add_subplot(gs[1, :])
        self._plot_category_temporal_evolution(ax3)

        # 4. Análisis detallado por categoría
        ax4 = fig.add_subplot(gs[2, :])
        self._create_category_growth_details_text(ax4)

    def _plot_category_revenue_growth_bars(self, ax):
        """Gráfico de crecimiento de ingresos por categoría"""
        category_names = []
        category_growth_jul = []
        colors = COLORS['categories']

        for category, data in self.stats['category_growth'].items():
            if 'Julio' in data['revenue_growth'].index:
                category_names.append(category)
                category_growth_jul.append(data['revenue_growth']['Julio'])

        if category_names:
            bars = ax.bar(category_names, category_growth_jul,
                          color=colors[:len(category_names)], alpha=0.8)
            ax.set_ylabel('Crecimiento (%)',
                          fontsize=FONT_SIZES['normal'], fontweight='bold')
            ax.set_title('CRECIMIENTO INGRESOS\n(Julio vs Junio)',
                         fontsize=FONT_SIZES['normal'], fontweight='bold')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax.grid(True, alpha=0.3)
            plt.setp(ax.get_xticklabels(), rotation=45,
                     ha='right', fontsize=FONT_SIZES['tiny'])

            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3 if height >= 0 else -15),
                            textcoords="offset points",
                            ha='center', va='bottom' if height >= 0 else 'top',
                            fontweight='bold', fontsize=FONT_SIZES['mini'])

    def _plot_category_count_growth_bars(self, ax):
        """Gráfico de crecimiento de cantidad por categoría"""
        category_names = []
        category_count_growth = []
        colors = COLORS['categories']

        for category, data in self.stats['category_growth'].items():
            if 'Julio' in data['count_growth'].index:
                category_names.append(category)
                category_count_growth.append(data['count_growth']['Julio'])

        if category_names:
            bars = ax.bar(category_names, category_count_growth,
                          color=colors[:len(category_names)], alpha=0.8)
            ax.set_ylabel('Crecimiento (%)',
                          fontsize=FONT_SIZES['normal'], fontweight='bold')
            ax.set_title('CRECIMIENTO CANTIDAD\n(Julio vs Junio)',
                         fontsize=FONT_SIZES['normal'], fontweight='bold')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax.grid(True, alpha=0.3)
            plt.setp(ax.get_xticklabels(), rotation=45,
                     ha='right', fontsize=FONT_SIZES['tiny'])

            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3 if height >= 0 else -15),
                            textcoords="offset points",
                            ha='center', va='bottom' if height >= 0 else 'top',
                            fontweight='bold', fontsize=FONT_SIZES['mini'])

    def _plot_category_temporal_evolution(self, ax):
        """Gráfico de evolución temporal por categoría"""
        category_evolution = self.combined_df.groupby(['month', 'category_clean'])[
            'amount'].sum().unstack(fill_value=0)
        colors = COLORS['categories']

        for i, category in enumerate(category_evolution.columns):
            ax.plot(category_evolution.index, category_evolution[category],
                    marker='o', linewidth=3, markersize=8, label=category,
                    color=colors[i])

        ax.set_title('EVOLUCION DE INGRESOS POR CATEGORIA (Mayo - Julio)',
                     fontsize=FONT_SIZES['section'], fontweight='bold')
        ax.set_ylabel('Ingresos (S/)',
                      fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.legend(fontsize=FONT_SIZES['small'], loc='upper left')
        ax.grid(True, alpha=0.3)

        # Agregar valores en los puntos
        for i, category in enumerate(category_evolution.columns):
            for j, (month, value) in enumerate(zip(category_evolution.index, category_evolution[category])):
                if value > 0:
                    ax.annotate(f'S/ {value:,.0f}', (j, value), textcoords="offset points",
                                xytext=(0, 10 + i*15), ha='center', fontweight='bold',
                                fontsize=FONT_SIZES['mini'], color=colors[i])

    def _create_category_growth_details_text(self, ax):
        """Crea el texto de análisis detallado por categoría"""
        ax.axis('off')

        growth_summary = "RESUMEN DE CRECIMIENTO POR CATEGORIA:\n\n"

        for category, data in self.stats['category_growth'].items():
            if len(data['revenue_growth']) >= 2:
                may_jun = data['revenue_growth']['Junio'] if 'Junio' in data['revenue_growth'].index else 0
                jun_jul = data['revenue_growth']['Julio'] if 'Julio' in data['revenue_growth'].index else 0
                growth_summary += f"  • Mayo → Junio: {may_jun:+.1f}%\n"
                growth_summary += f"  • Junio → Julio: {jun_jul:+.1f}%\n\n"

        ax.text(0.02, 0.98, growth_summary, fontsize=FONT_SIZES['small'], fontweight='bold',
                verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f8f8", alpha=0.9))
