"""
Módulo para crear visualizaciones y gráficos
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .config import COLORS, FONT_SIZES, GRID_CONFIG


class MembershipVisualizations:
    """Maneja la creación de todos los gráficos del reporte"""

    def __init__(self, combined_df, monthly_summary, stats):
        self.combined_df = combined_df
        self.monthly_summary = monthly_summary
        self.stats = stats

    def create_monthly_comparison_page(self, fig):
        """Crea los gráficos de comparación mensual"""
        axes = fig.subplots(2, 2)

        # 1. Ingresos por mes
        self._plot_monthly_revenue(axes[0, 0])

        # 2. Número de membresías por mes
        self._plot_monthly_memberships(axes[0, 1])

        # 3. Ticket promedio por mes
        self._plot_monthly_tickets(axes[1, 0])

        # 4. Distribución de planes por mes
        self._plot_plan_distribution_by_month(axes[1, 1])

        plt.tight_layout()

    def _plot_monthly_revenue(self, ax):
        """Gráfico de ingresos mensuales"""
        months = self.monthly_summary['month']
        revenue = self.monthly_summary['ingresos_total']

        bars = ax.bar(months, revenue, color=COLORS['primary'])
        ax.set_title('Ingresos Totales por Mes',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_ylabel('Ingresos (S/)', fontsize=FONT_SIZES['normal'])

        # Agregar valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'S/ {height:,.0f}', ha='center', va='bottom',
                    fontweight='bold', fontsize=FONT_SIZES['small'])

    def _plot_monthly_memberships(self, ax):
        """Gráfico de número de membresías mensuales"""
        months = self.monthly_summary['month']
        memberships = self.monthly_summary['total_membresías']

        bars = ax.bar(months, memberships, color=COLORS['primary'])
        ax.set_title('Número de Membresías por Mes',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_ylabel('Cantidad', fontsize=FONT_SIZES['normal'])

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(height)}', ha='center', va='bottom',
                    fontweight='bold', fontsize=FONT_SIZES['small'])

    def _plot_monthly_tickets(self, ax):
        """Gráfico de ticket promedio mensual"""
        months = self.monthly_summary['month']
        tickets = self.monthly_summary['ticket_promedio']

        bars = ax.bar(months, tickets, color=COLORS['primary'])
        ax.set_title('Ticket Promedio por Mes',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_ylabel('Ticket Promedio (S/)', fontsize=FONT_SIZES['normal'])

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'S/ {height:,.0f}', ha='center', va='bottom',
                    fontweight='bold', fontsize=FONT_SIZES['small'])

    def _plot_plan_distribution_by_month(self, ax):
        """Gráfico de distribución de planes por mes"""
        plan_by_month = pd.crosstab(
            self.combined_df['month'],
            self.combined_df['membership_plan_name']
        )
        plan_by_month.plot(kind='bar', ax=ax, stacked=True,
                           color=COLORS['plans'])
        ax.set_title('Distribución de Planes por Mes',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_ylabel('Cantidad', fontsize=FONT_SIZES['normal'])
        ax.set_xlabel('Mes', fontsize=FONT_SIZES['normal'])
        ax.legend(title='Plan de Membresía',
                  bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.tick_params(axis='x', rotation=0)

    def create_plan_analysis_page(self, fig):
        """Crea los gráficos de análisis por planes"""
        axes = fig.subplots(2, 2)

        # 1. Ingresos por plan
        self._plot_plan_revenue(axes[0, 0])

        # 2. Cantidad por plan
        self._plot_plan_count(axes[0, 1])

        # 3. Distribución porcentual
        self._plot_plan_distribution_pie(axes[1, 0])

        # 4. Evolución temporal por plan
        self._plot_plan_evolution(axes[1, 1])

        plt.tight_layout()

    def _plot_plan_revenue(self, ax):
        """Gráfico horizontal de ingresos por plan"""
        plan_revenue = self.stats['by_plan']['ingresos'].sort_values(
            ascending=True)
        bars = ax.barh(plan_revenue.index, plan_revenue.values,
                       color=COLORS['secondary'][:len(plan_revenue)])
        ax.set_title('Ingresos por Plan de Membresía',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_xlabel('Ingresos (S/)', fontsize=FONT_SIZES['normal'])

        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'S/ {width:,.0f}', ha='left', va='center',
                    fontweight='bold', fontsize=FONT_SIZES['small'])

    def _plot_plan_count(self, ax):
        """Gráfico horizontal de cantidad por plan"""
        plan_count = self.stats['by_plan']['cantidad'].sort_values(
            ascending=True)
        bars = ax.barh(plan_count.index, plan_count.values,
                       color=COLORS['secondary'][:len(plan_count)])
        ax.set_title('Cantidad de Membresías por Plan',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_xlabel('Cantidad', fontsize=FONT_SIZES['normal'])

        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'{int(width)}', ha='left', va='center',
                    fontweight='bold', fontsize=FONT_SIZES['small'])

    def _plot_plan_distribution_pie(self, ax):
        """Gráfico circular de distribución de planes"""
        plan_distribution = self.combined_df['membership_plan_name'].value_counts(
        )
        wedges, texts, autotexts = ax.pie(
            plan_distribution.values,
            labels=plan_distribution.index,
            autopct='%1.1f%%',
            colors=COLORS['plans'][:len(plan_distribution)],
            startangle=90
        )
        ax.set_title('Distribución de Planes de Membresía',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')

    def _plot_plan_evolution(self, ax):
        """Gráfico de evolución temporal por plan"""
        plan_evolution = self.combined_df.groupby(['month', 'membership_plan_name'])[
            'amount'].sum().unstack(fill_value=0)
        plan_evolution.plot(kind='line', ax=ax, marker='o', linewidth=2,
                            markersize=8, color=COLORS['plans'])
        ax.set_title('Evolución de Ingresos por Plan',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_ylabel('Ingresos (S/)', fontsize=FONT_SIZES['normal'])
        ax.set_xlabel('Mes', fontsize=FONT_SIZES['normal'])
        ax.legend(title='Plan de Membresía',
                  bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)

    def create_growth_overview_page(self, fig):
        """Crea la página de vista general de crecimiento"""
        gs = fig.add_gridspec(
            2, 2, hspace=GRID_CONFIG['hspace'], wspace=GRID_CONFIG['wspace'])

        # 1. Evolución principal (gráfico más grande)
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_main_evolution(ax1)

        # 2. Resumen de crecimiento
        ax2 = fig.add_subplot(gs[1, 0])
        self._create_growth_summary_text(ax2)

        # 3. Proyecciones
        ax3 = fig.add_subplot(gs[1, 1])
        self._create_projections_text(ax3)

    def _plot_main_evolution(self, ax):
        """Gráfico principal de evolución con doble eje Y"""
        months = self.monthly_summary['month'].tolist()
        revenue = self.monthly_summary['ingresos_total'].tolist()
        memberships = self.monthly_summary['total_membresías'].tolist()

        ax_twin = ax.twinx()

        # Línea de ingresos
        line1 = ax.plot(months, revenue, color='#FF6B6B', marker='o',
                        linewidth=4, markersize=12, label='Ingresos (S/)')
        ax.set_ylabel('Ingresos (S/)', color='#FF6B6B',
                      fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.tick_params(axis='y', labelcolor='#FF6B6B',
                       labelsize=FONT_SIZES['normal'])

        # Línea de membresías
        line2 = ax_twin.plot(months, memberships, color='#4ECDC4', marker='s',
                             linewidth=4, markersize=12, label='Membresías')
        ax_twin.set_ylabel('Número de Membresías', color='#4ECDC4',
                           fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax_twin.tick_params(axis='y', labelcolor='#4ECDC4',
                            labelsize=FONT_SIZES['normal'])

        ax.set_title('EVOLUCION MENSUAL - INGRESOS Y MEMBRESIAS',
                     fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', labelsize=FONT_SIZES['normal'])

        # Agregar valores en los puntos
        for i, (month, rev, mem) in enumerate(zip(months, revenue, memberships)):
            ax.annotate(f'S/ {rev:,.0f}', (i, rev), textcoords="offset points",
                        xytext=(0, 20), ha='center', fontweight='bold',
                        color='#FF6B6B', fontsize=FONT_SIZES['normal'])
            ax_twin.annotate(f'{mem}', (i, mem), textcoords="offset points",
                             xytext=(0, -25), ha='center', fontweight='bold',
                             color='#4ECDC4', fontsize=FONT_SIZES['normal'])

    def _create_growth_summary_text(self, ax):
        """Crea el texto de resumen de crecimiento"""
        ax.axis('off')

        months = self.monthly_summary['month'].tolist()
        revenue = self.monthly_summary['ingresos_total'].tolist()
        memberships = self.monthly_summary['total_membresías'].tolist()

        total_growth_revenue = ((revenue[-1] - revenue[0]) / revenue[0]) * 100
        total_growth_memberships = (
            (memberships[-1] - memberships[0]) / memberships[0]) * 100
        total_change_revenue = revenue[-1] - revenue[0]
        total_change_memberships = memberships[-1] - memberships[0]

        summary_text = f"""
CRECIMIENTO TOTAL (Mayo - Julio):

INGRESOS:
• Crecimiento: {total_growth_revenue:+.1f}%
• Cambio: S/ {total_change_revenue:+,.0f}
• De S/ {revenue[0]:,.0f} a S/ {revenue[-1]:,.0f}

MEMBRESIAS:
• Crecimiento: {total_growth_memberships:+.1f}%
• Cambio: {total_change_memberships:+.0f} membresias
• De {memberships[0]} a {memberships[-1]} membresias

MEJOR MES: {self.stats['trends']['mejor_mes_ingresos']}
PEOR MES: {self.stats['trends']['peor_mes_ingresos']}
        """

        ax.text(0.05, 0.95, summary_text, fontsize=FONT_SIZES['normal'],
                fontweight='bold', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f4fd", alpha=0.9))

    def _create_projections_text(self, ax):
        """Crea el texto de proyecciones"""
        ax.axis('off')

        projection_text = f"""
PROYECCIONES AGOSTO:

INGRESOS ESTIMADOS:
• S/ {self.stats['projections']['agosto_ingresos_estimados']:,.0f}
• Tendencia: {self.stats['projections']['tendencia_ingresos']}

MEMBRESIAS ESTIMADAS:
• {self.stats['projections']['agosto_membresias_estimadas']:.0f} membresias
• Tendencia: {self.stats['projections']['tendencia_membresias']}

PROMEDIO CRECIMIENTO:
• Ingresos: {self.stats['trends']['promedio_crecimiento_ingresos']:.1f}% mensual
• Membresias: {self.stats['trends']['promedio_crecimiento_membresias']:.1f}% mensual
        """

        ax.text(0.05, 0.95, projection_text, fontsize=FONT_SIZES['normal'],
                fontweight='bold', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff2e8", alpha=0.9))

    def create_monthly_growth_page(self, fig):
        """Crea la página de crecimiento mensual detallado"""
        gs = fig.add_gridspec(2, 2, hspace=GRID_CONFIG['detailed_hspace'],
                              wspace=GRID_CONFIG['wspace'])

        # 1. Tasas de crecimiento
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_growth_rates(ax1)

        # 2. Cambios absolutos
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_absolute_changes(ax2)

        # 3. Evolución del ticket promedio
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_ticket_evolution(ax3)

        # 4. Detalles mensuales
        ax4 = fig.add_subplot(gs[1, 1])
        self._create_monthly_details_text(ax4)

    def _plot_growth_rates(self, ax):
        """Gráfico de tasas de crecimiento porcentual"""
        growth_data = {
            'Ingresos': [self.stats['growth_rates']['ingresos']['Junio'],
                         self.stats['growth_rates']['ingresos']['Julio']],
            'Membresias': [self.stats['growth_rates']['membresias']['Junio'],
                           self.stats['growth_rates']['membresias']['Julio']]
        }

        x_pos = np.arange(len(['Jun vs May', 'Jul vs Jun']))
        width = 0.35

        bars1 = ax.bar(x_pos - width/2, growth_data['Ingresos'], width,
                       label='Ingresos', color='#FF6B6B', alpha=0.8)
        bars2 = ax.bar(x_pos + width/2, growth_data['Membresias'], width,
                       label='Membresias', color='#4ECDC4', alpha=0.8)

        ax.set_ylabel('Crecimiento (%)',
                      fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_title('TASAS DE CRECIMIENTO MENSUAL',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(['Jun vs May', 'Jul vs Jun'],
                           fontsize=FONT_SIZES['small'])
        ax.legend(fontsize=FONT_SIZES['small'])
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.grid(True, alpha=0.3)

        # Agregar valores en las barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3 if height >= 0 else -15),
                            textcoords="offset points",
                            ha='center', va='bottom' if height >= 0 else 'top',
                            fontweight='bold', fontsize=FONT_SIZES['tiny'])

    def _plot_absolute_changes(self, ax):
        """Gráfico de cambios absolutos en ingresos"""
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
        ax.set_title('CAMBIO EN INGRESOS (Soles)',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
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

    def _plot_ticket_evolution(self, ax):
        """Gráfico de evolución del ticket promedio"""
        months = self.monthly_summary['month'].tolist()
        tickets = self.monthly_summary['ticket_promedio'].tolist()

        ax.plot(months, tickets, color='#45B7D1', marker='D',
                linewidth=4, markersize=10)
        ax.set_ylabel('Ticket Promedio (S/)',
                      fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_title('EVOLUCION TICKET PROMEDIO',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', labelsize=FONT_SIZES['small'])

        for i, (month, ticket) in enumerate(zip(months, tickets)):
            ax.annotate(f'S/ {ticket:,.0f}', (i, ticket),
                        textcoords="offset points", xytext=(0, 15),
                        ha='center', fontweight='bold', fontsize=FONT_SIZES['small'])

    def _create_monthly_details_text(self, ax):
        """Crea el texto de detalles mensuales"""
        ax.axis('off')

        details_text = f"""
DETALLES MES A MES:

MAYO → JUNIO:
• Ingresos: {self.stats['growth_rates']['ingresos']['Junio']:+.1f}%
• Membresias: {self.stats['growth_rates']['membresias']['Junio']:+.1f}%
• Ticket Prom: {self.stats['growth_rates']['ticket_promedio']['Junio']:+.1f}%
• Clientes: {self.stats['growth_rates']['clientes_unicos']['Junio']:+.1f}%

JUNIO → JULIO:
• Ingresos: {self.stats['growth_rates']['ingresos']['Julio']:+.1f}%
• Membresias: {self.stats['growth_rates']['membresias']['Julio']:+.1f}%
• Ticket Prom: {self.stats['growth_rates']['ticket_promedio']['Julio']:+.1f}%
• Clientes: {self.stats['growth_rates']['clientes_unicos']['Julio']:+.1f}%
        """

        ax.text(0.05, 0.95, details_text, fontsize=FONT_SIZES['small'],
                fontweight='bold', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f8e8", alpha=0.9))

    def create_plan_growth_page(self, fig):
        """Crea la página de crecimiento por planes"""
        gs = fig.add_gridspec(2, 2, hspace=GRID_CONFIG['detailed_hspace'],
                              wspace=GRID_CONFIG['wspace'])

        # 1. Crecimiento de ingresos por plan
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_plan_revenue_growth(ax1)

        # 2. Crecimiento de cantidad por plan
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_plan_count_growth(ax2)

        # 3. Evolución temporal completa por plan
        ax3 = fig.add_subplot(gs[1, :])
        self._plot_plan_temporal_evolution(ax3)

    def _plot_plan_revenue_growth(self, ax):
        """Gráfico de crecimiento de ingresos por plan (Julio vs Junio)"""
        plan_names = []
        plan_growth_jul = []

        for plan, data in self.stats['plan_growth'].items():
            if 'Julio' in data['revenue_growth'].index:
                plan_names.append(plan)
                plan_growth_jul.append(data['revenue_growth']['Julio'])

        if plan_names:
            bars = ax.bar(plan_names, plan_growth_jul,
                          color=COLORS['plans'][:len(plan_names)], alpha=0.8)
            ax.set_ylabel('Crecimiento Ingresos (%)',
                          fontsize=FONT_SIZES['normal'], fontweight='bold')
            ax.set_title('CRECIMIENTO INGRESOS POR PLAN\n(Julio vs Junio)',
                         fontsize=FONT_SIZES['subtitle'], fontweight='bold')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=0, labelsize=FONT_SIZES['small'])

            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3 if height >= 0 else -15),
                            textcoords="offset points",
                            ha='center', va='bottom' if height >= 0 else 'top',
                            fontweight='bold', fontsize=FONT_SIZES['small'])

    def _plot_plan_count_growth(self, ax):
        """Gráfico de crecimiento de cantidad por plan"""
        plan_names = []
        plan_count_growth = []

        for plan, data in self.stats['plan_growth'].items():
            if 'Julio' in data['count_growth'].index:
                plan_names.append(plan)
                plan_count_growth.append(data['count_growth']['Julio'])

        if plan_names:
            bars = ax.bar(plan_names, plan_count_growth,
                          color=COLORS['plans'][:len(plan_names)], alpha=0.8)
            ax.set_ylabel('Crecimiento Cantidad (%)',
                          fontsize=FONT_SIZES['normal'], fontweight='bold')
            ax.set_title('CRECIMIENTO CANTIDAD POR PLAN\n(Julio vs Junio)',
                         fontsize=FONT_SIZES['subtitle'], fontweight='bold')
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=0, labelsize=FONT_SIZES['small'])

            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3 if height >= 0 else -15),
                            textcoords="offset points",
                            ha='center', va='bottom' if height >= 0 else 'top',
                            fontweight='bold', fontsize=FONT_SIZES['small'])

    def _plot_plan_temporal_evolution(self, ax):
        """Gráfico de evolución temporal de ingresos por plan"""
        plan_evolution = self.combined_df.groupby(['month', 'membership_plan_name'])[
            'amount'].sum().unstack(fill_value=0)

        for i, plan in enumerate(plan_evolution.columns):
            ax.plot(plan_evolution.index, plan_evolution[plan],
                    marker='o', linewidth=3, markersize=8, label=plan,
                    color=COLORS['plans'][i])

        ax.set_title('EVOLUCION DE INGRESOS POR PLAN (Mayo - Julio)',
                     fontsize=FONT_SIZES['subtitle'], fontweight='bold')
        ax.set_ylabel('Ingresos (S/)',
                      fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.set_xlabel('Mes', fontsize=FONT_SIZES['normal'], fontweight='bold')
        ax.legend(fontsize=FONT_SIZES['small'], loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', labelsize=FONT_SIZES['small'])

        # Agregar valores en los puntos
        for i, plan in enumerate(plan_evolution.columns):
            for j, (month, value) in enumerate(zip(plan_evolution.index, plan_evolution[plan])):
                if value > 0:
                    ax.annotate(f'S/ {value:,.0f}', (j, value),
                                textcoords="offset points",
                                xytext=(0, 10 + i*15), ha='center',
                                fontweight='bold', fontsize=FONT_SIZES['tiny'],
                                color=COLORS['plans'][i])
