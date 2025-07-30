#!/usr/bin/env python3
"""
Generador de Reporte PDF - Análisis de Membresías
Analiza datos de membresías de mayo, junio y julio 2024
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from datetime import datetime
import os
from collections import Counter

# Configuración de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class MembershipReportGenerator:
    def __init__(self, data_path="data/membership/"):
        self.data_path = data_path
        self.months = ['mayo', 'junio', 'julio']
        self.month_names = {'mayo': 'Mayo', 'junio': 'Junio', 'julio': 'Julio'}
        self.dfs = {}

    def load_data(self):
        """Carga los datos de los 3 meses"""
        for month in self.months:
            file_path = f"{self.data_path}membership-{month}.csv"
            try:
                df = pd.read_csv(file_path)
                df['month'] = self.month_names[month]
                df['month_order'] = self.months.index(month) + 1
                self.dfs[month] = df
                print(f"Cargado: {file_path} - {len(df)} registros")
            except FileNotFoundError:
                print(f"No se encontro: {file_path}")

    def prepare_data(self):
        """Prepara y combina los datos"""
        if not self.dfs:
            raise ValueError(
                "No se cargaron datos. Ejecuta load_data() primero.")

        # Combinar todos los dataframes
        self.combined_df = pd.concat(self.dfs.values(), ignore_index=True)

        # Limpiar y estandarizar datos
        self.combined_df['membership_plan_name'] = self.combined_df['membership_plan_name'].str.strip()
        self.combined_df['amount'] = pd.to_numeric(
            self.combined_df['amount'], errors='coerce')

        # Crear resumen por mes
        self.monthly_summary = self.combined_df.groupby(['month', 'month_order']).agg({
            'amount': ['sum', 'mean', 'count'],
            'email': 'nunique'
        }).round(2)

        self.monthly_summary.columns = [
            'ingresos_total', 'ticket_promedio', 'total_membresías', 'clientes_únicos']
        self.monthly_summary = self.monthly_summary.reset_index().sort_values('month_order')

    def create_summary_stats(self):
        """Genera estadísticas de resumen"""
        stats = {}

        # Estadísticas generales
        stats['total_revenue'] = self.combined_df['amount'].sum()
        stats['total_memberships'] = len(self.combined_df)
        stats['unique_customers'] = self.combined_df['email'].nunique()
        stats['avg_ticket'] = self.combined_df['amount'].mean()

        # Por plan
        plan_stats = self.combined_df.groupby('membership_plan_name').agg({
            'amount': ['sum', 'count', 'mean'],
            'email': 'nunique'
        }).round(2)
        plan_stats.columns = ['ingresos', 'cantidad',
                              'ticket_promedio', 'clientes_únicos']
        stats['by_plan'] = plan_stats.sort_values('ingresos', ascending=False)

        # Análisis de crecimiento detallado
        monthly_revenue = self.monthly_summary.set_index('month')[
            'ingresos_total']
        monthly_memberships = self.monthly_summary.set_index('month')[
            'total_membresías']
        monthly_tickets = self.monthly_summary.set_index('month')[
            'ticket_promedio']
        monthly_customers = self.monthly_summary.set_index('month')[
            'clientes_únicos']

        # Tasas de crecimiento
        stats['growth_rates'] = {
            'ingresos': monthly_revenue.pct_change().fillna(0) * 100,
            'membresias': monthly_memberships.pct_change().fillna(0) * 100,
            'ticket_promedio': monthly_tickets.pct_change().fillna(0) * 100,
            'clientes_unicos': monthly_customers.pct_change().fillna(0) * 100
        }

        # Cambios absolutos
        stats['absolute_changes'] = {
            'ingresos': monthly_revenue.diff().fillna(0),
            'membresias': monthly_memberships.diff().fillna(0),
            'ticket_promedio': monthly_tickets.diff().fillna(0),
            'clientes_unicos': monthly_customers.diff().fillna(0)
        }

        # Análisis de tendencias
        stats['trends'] = {
            'mejor_mes_ingresos': monthly_revenue.idxmax(),
            'peor_mes_ingresos': monthly_revenue.idxmin(),
            'mejor_mes_membresias': monthly_memberships.idxmax(),
            'mayor_crecimiento_ingresos': stats['growth_rates']['ingresos'].idxmax(),
            'mayor_caida_ingresos': stats['growth_rates']['ingresos'].idxmin(),
            'promedio_crecimiento_ingresos': stats['growth_rates']['ingresos'].mean(),
            'promedio_crecimiento_membresias': stats['growth_rates']['membresias'].mean()
        }

        # Análisis por planes - crecimiento
        plan_evolution = {}
        for plan in self.combined_df['membership_plan_name'].unique():
            plan_data = self.combined_df[self.combined_df['membership_plan_name'] == plan]
            plan_monthly = plan_data.groupby('month').agg({
                'amount': 'sum',
                'email': 'count'
            })

            if len(plan_monthly) > 1:
                plan_evolution[plan] = {
                    'revenue_growth': plan_monthly['amount'].pct_change().fillna(0) * 100,
                    'count_growth': plan_monthly['email'].pct_change().fillna(0) * 100,
                    'revenue_change': plan_monthly['amount'].diff().fillna(0)
                }

        stats['plan_growth'] = plan_evolution

        # Predicciones simples (proyección lineal)
        if len(monthly_revenue) >= 2:
            # Calcular tendencia para agosto
            revenue_trend = (
                monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2])
            membership_trend = (
                monthly_memberships.iloc[-1] - monthly_memberships.iloc[-2])

            stats['projections'] = {
                'agosto_ingresos_estimados': monthly_revenue.iloc[-1] + revenue_trend,
                'agosto_membresias_estimadas': monthly_memberships.iloc[-1] + membership_trend,
                'tendencia_ingresos': 'Creciente' if revenue_trend > 0 else 'Decreciente',
                'tendencia_membresias': 'Creciente' if membership_trend > 0 else 'Decreciente'
            }

        self.stats = stats

    def plot_monthly_comparison(self, fig, axes):
        """Gráficos de comparación mensual"""

        # 1. Ingresos por mes
        ax1 = axes[0, 0]
        bars1 = ax1.bar(self.monthly_summary['month'], self.monthly_summary['ingresos_total'],
                        color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax1.set_title('Ingresos Totales por Mes',
                      fontsize=14, fontweight='bold')
        ax1.set_ylabel('Ingresos (S/)', fontsize=12)

        # Agregar valores en las barras
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                     f'S/ {height:,.0f}', ha='center', va='bottom', fontweight='bold')

        # 2. Número de membresías por mes
        ax2 = axes[0, 1]
        bars2 = ax2.bar(self.monthly_summary['month'], self.monthly_summary['total_membresías'],
                        color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax2.set_title('Número de Membresías por Mes',
                      fontsize=14, fontweight='bold')
        ax2.set_ylabel('Cantidad', fontsize=12)

        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                     f'{int(height)}', ha='center', va='bottom', fontweight='bold')

        # 3. Ticket promedio por mes
        ax3 = axes[1, 0]
        bars3 = ax3.bar(self.monthly_summary['month'], self.monthly_summary['ticket_promedio'],
                        color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax3.set_title('Ticket Promedio por Mes',
                      fontsize=14, fontweight='bold')
        ax3.set_ylabel('Ticket Promedio (S/)', fontsize=12)

        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                     f'S/ {height:,.0f}', ha='center', va='bottom', fontweight='bold')

        # 4. Distribución de planes por mes
        ax4 = axes[1, 1]
        plan_by_month = pd.crosstab(
            self.combined_df['month'], self.combined_df['membership_plan_name'])
        plan_by_month.plot(kind='bar', ax=ax4, stacked=True)
        ax4.set_title('Distribución de Planes por Mes',
                      fontsize=14, fontweight='bold')
        ax4.set_ylabel('Cantidad', fontsize=12)
        ax4.set_xlabel('Mes', fontsize=12)
        ax4.legend(title='Plan de Membresía',
                   bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.tick_params(axis='x', rotation=0)

        plt.tight_layout()

    def plot_plan_analysis(self, fig, axes):
        """Análisis por planes de membresía"""

        # 1. Ingresos por plan
        ax1 = axes[0, 0]
        plan_revenue = self.stats['by_plan']['ingresos'].sort_values(
            ascending=True)
        bars1 = ax1.barh(plan_revenue.index, plan_revenue.values,
                         color=['#96CEB4', '#FECA57', '#FF9FF3'])
        ax1.set_title('Ingresos por Plan de Membresía',
                      fontsize=14, fontweight='bold')
        ax1.set_xlabel('Ingresos (S/)', fontsize=12)

        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                     f'S/ {width:,.0f}', ha='left', va='center', fontweight='bold')

        # 2. Cantidad por plan
        ax2 = axes[0, 1]
        plan_count = self.stats['by_plan']['cantidad'].sort_values(
            ascending=True)
        bars2 = ax2.barh(plan_count.index, plan_count.values,
                         color=['#96CEB4', '#FECA57', '#FF9FF3'])
        ax2.set_title('Cantidad de Membresías por Plan',
                      fontsize=14, fontweight='bold')
        ax2.set_xlabel('Cantidad', fontsize=12)

        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                     f'{int(width)}', ha='left', va='center', fontweight='bold')

        # 3. Distribución porcentual de planes
        ax3 = axes[1, 0]
        plan_distribution = self.combined_df['membership_plan_name'].value_counts(
        )
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        wedges, texts, autotexts = ax3.pie(plan_distribution.values, labels=plan_distribution.index,
                                           autopct='%1.1f%%', colors=colors, startangle=90)
        ax3.set_title('Distribución de Planes de Membresía',
                      fontsize=14, fontweight='bold')

        # 4. Evolución de ingresos por plan
        ax4 = axes[1, 1]
        plan_evolution = self.combined_df.groupby(['month', 'membership_plan_name'])[
            'amount'].sum().unstack(fill_value=0)
        plan_evolution.plot(kind='line', ax=ax4, marker='o',
                            linewidth=2, markersize=8)
        ax4.set_title('Evolución de Ingresos por Plan',
                      fontsize=14, fontweight='bold')
        ax4.set_ylabel('Ingresos (S/)', fontsize=12)
        ax4.set_xlabel('Mes', fontsize=12)
        ax4.legend(title='Plan de Membresía',
                   bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

    def create_growth_overview_page(self, fig):
        """Página 1 del análisis de crecimiento - Vista general"""

        # Crear grid de 2x2
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. Evolución de ingresos y membresías (gráfico principal más grande)
        ax1 = fig.add_subplot(gs[0, :])
        months = self.monthly_summary['month'].tolist()
        revenue = self.monthly_summary['ingresos_total'].tolist()
        memberships = self.monthly_summary['total_membresías'].tolist()

        ax1_twin = ax1.twinx()

        line1 = ax1.plot(months, revenue, color='#FF6B6B', marker='o', linewidth=4,
                         markersize=12, label='Ingresos (S/)')
        ax1.set_ylabel('Ingresos (S/)', color='#FF6B6B',
                       fontsize=14, fontweight='bold')
        ax1.tick_params(axis='y', labelcolor='#FF6B6B', labelsize=12)

        line2 = ax1_twin.plot(months, memberships, color='#4ECDC4', marker='s', linewidth=4,
                              markersize=12, label='Membresías')
        ax1_twin.set_ylabel('Número de Membresías',
                            color='#4ECDC4', fontsize=14, fontweight='bold')
        ax1_twin.tick_params(axis='y', labelcolor='#4ECDC4', labelsize=12)

        ax1.set_title('EVOLUCION MENSUAL - INGRESOS Y MEMBRESIAS',
                      fontsize=16, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', labelsize=12)

        # Agregar valores en los puntos más grandes
        for i, (month, rev, mem) in enumerate(zip(months, revenue, memberships)):
            ax1.annotate(f'S/ {rev:,.0f}', (i, rev), textcoords="offset points",
                         xytext=(0, 20), ha='center', fontweight='bold', color='#FF6B6B', fontsize=12)
            ax1_twin.annotate(f'{mem}', (i, mem), textcoords="offset points",
                              xytext=(0, -25), ha='center', fontweight='bold', color='#4ECDC4', fontsize=12)

        # 2. Resumen de crecimiento total
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.axis('off')

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

        ax2.text(0.05, 0.95, summary_text, fontsize=12, fontweight='bold',
                 verticalalignment='top', transform=ax2.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f4fd", alpha=0.9))

        # 3. Proyecciones para agosto
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.axis('off')

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

        ax3.text(0.05, 0.95, projection_text, fontsize=12, fontweight='bold',
                 verticalalignment='top', transform=ax3.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff2e8", alpha=0.9))

    def create_monthly_growth_page(self, fig):
        """Página 2 del análisis de crecimiento - Análisis mensual detallado"""

        # Crear grid de 2x2
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

        # 1. Tasas de crecimiento porcentual
        ax1 = fig.add_subplot(gs[0, 0])
        growth_data = {
            'Ingresos': [self.stats['growth_rates']['ingresos']['Junio'],
                         self.stats['growth_rates']['ingresos']['Julio']],
            'Membresias': [self.stats['growth_rates']['membresias']['Junio'],
                           self.stats['growth_rates']['membresias']['Julio']]
        }

        x_pos = np.arange(len(['Jun vs May', 'Jul vs Jun']))
        width = 0.35

        bars1 = ax1.bar(x_pos - width/2, growth_data['Ingresos'], width,
                        label='Ingresos', color='#FF6B6B', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, growth_data['Membresias'], width,
                        label='Membresias', color='#4ECDC4', alpha=0.8)

        ax1.set_ylabel('Crecimiento (%)', fontsize=12, fontweight='bold')
        ax1.set_title('TASAS DE CRECIMIENTO MENSUAL',
                      fontsize=14, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(['Jun vs May', 'Jul vs Jun'], fontsize=11)
        ax1.legend(fontsize=11)
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.grid(True, alpha=0.3)

        # Agregar valores en las barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3 if height >= 0 else -15), textcoords="offset points",
                             ha='center', va='bottom' if height >= 0 else 'top',
                             fontweight='bold', fontsize=10)

        # 2. Cambios absolutos en ingresos
        ax2 = fig.add_subplot(gs[0, 1])
        revenue_changes = [
            self.stats['absolute_changes']['ingresos']['Junio'],
            self.stats['absolute_changes']['ingresos']['Julio']
        ]
        colors = ['green' if x >= 0 else 'red' for x in revenue_changes]
        bars2 = ax2.bar(['Jun vs May', 'Jul vs Jun'],
                        revenue_changes, color=colors, alpha=0.7)
        ax2.set_ylabel('Cambio Absoluto (S/)', fontsize=12, fontweight='bold')
        ax2.set_title('CAMBIO EN INGRESOS (Soles)',
                      fontsize=14, fontweight='bold')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.grid(True, alpha=0.3)

        for bar in bars2:
            height = bar.get_height()
            ax2.annotate(f'S/ {height:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3 if height >= 0 else -15), textcoords="offset points",
                         ha='center', va='bottom' if height >= 0 else 'top',
                         fontweight='bold', fontsize=10)

        # 3. Evolución del ticket promedio
        ax3 = fig.add_subplot(gs[1, 0])
        months = self.monthly_summary['month'].tolist()
        tickets = self.monthly_summary['ticket_promedio'].tolist()
        ticket_changes = [
            self.stats['growth_rates']['ticket_promedio']['Junio'],
            self.stats['growth_rates']['ticket_promedio']['Julio']
        ]

        ax3.plot(months, tickets, color='#45B7D1',
                 marker='D', linewidth=4, markersize=10)
        ax3.set_ylabel('Ticket Promedio (S/)', fontsize=12, fontweight='bold')
        ax3.set_title('EVOLUCION TICKET PROMEDIO',
                      fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='both', labelsize=11)

        for i, (month, ticket) in enumerate(zip(months, tickets)):
            ax3.annotate(f'S/ {ticket:,.0f}', (i, ticket), textcoords="offset points",
                         xytext=(0, 15), ha='center', fontweight='bold', fontsize=11)

        # 4. Panel de detalles mensuales
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')

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

        ax4.text(0.05, 0.95, details_text, fontsize=11, fontweight='bold',
                 verticalalignment='top', transform=ax4.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f8e8", alpha=0.9))

    def create_plan_growth_page(self, fig):
        """Página 3 del análisis de crecimiento - Crecimiento por planes"""

        # Crear grid de 2x2
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

        # 1. Crecimiento de ingresos por plan (Julio vs Junio)
        ax1 = fig.add_subplot(gs[0, 0])
        plan_names = []
        plan_growth_jul = []
        plan_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

        for i, (plan, data) in enumerate(self.stats['plan_growth'].items()):
            if 'Julio' in data['revenue_growth'].index:
                plan_names.append(plan)
                plan_growth_jul.append(data['revenue_growth']['Julio'])

        if plan_names:
            bars1 = ax1.bar(plan_names, plan_growth_jul,
                            color=plan_colors[:len(plan_names)], alpha=0.8)
            ax1.set_ylabel('Crecimiento Ingresos (%)',
                           fontsize=12, fontweight='bold')
            ax1.set_title('CRECIMIENTO INGRESOS POR PLAN\n(Julio vs Junio)',
                          fontsize=14, fontweight='bold')
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=0, labelsize=11)

            for bar in bars1:
                height = bar.get_height()
                ax1.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3 if height >= 0 else -15), textcoords="offset points",
                             ha='center', va='bottom' if height >= 0 else 'top',
                             fontweight='bold', fontsize=11)

        # 2. Crecimiento de cantidad por plan
        ax2 = fig.add_subplot(gs[0, 1])
        plan_count_growth = []

        for plan in plan_names:
            if plan in self.stats['plan_growth'] and 'Julio' in self.stats['plan_growth'][plan]['count_growth'].index:
                plan_count_growth.append(
                    self.stats['plan_growth'][plan]['count_growth']['Julio'])
            else:
                plan_count_growth.append(0)

        if plan_names:
            bars2 = ax2.bar(plan_names, plan_count_growth,
                            color=plan_colors[:len(plan_names)], alpha=0.8)
            ax2.set_ylabel('Crecimiento Cantidad (%)',
                           fontsize=12, fontweight='bold')
            ax2.set_title('CRECIMIENTO CANTIDAD POR PLAN\n(Julio vs Junio)',
                          fontsize=14, fontweight='bold')
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=0, labelsize=11)

            for bar in bars2:
                height = bar.get_height()
                ax2.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3 if height >= 0 else -15), textcoords="offset points",
                             ha='center', va='bottom' if height >= 0 else 'top',
                             fontweight='bold', fontsize=11)

        # 3. Evolución temporal de ingresos por plan
        ax3 = fig.add_subplot(gs[1, :])
        plan_evolution = self.combined_df.groupby(['month', 'membership_plan_name'])[
            'amount'].sum().unstack(fill_value=0)

        for i, plan in enumerate(plan_evolution.columns):
            ax3.plot(plan_evolution.index, plan_evolution[plan],
                     marker='o', linewidth=3, markersize=8, label=plan, color=plan_colors[i])

        ax3.set_title('EVOLUCION DE INGRESOS POR PLAN (Mayo - Julio)',
                      fontsize=14, fontweight='bold')
        ax3.set_ylabel('Ingresos (S/)', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Mes', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=11, loc='upper left')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='both', labelsize=11)

        # Agregar valores en los puntos
        for i, plan in enumerate(plan_evolution.columns):
            for j, (month, value) in enumerate(zip(plan_evolution.index, plan_evolution[plan])):
                if value > 0:
                    ax3.annotate(f'S/ {value:,.0f}', (j, value), textcoords="offset points",
                                 xytext=(0, 10 + i*15), ha='center', fontweight='bold',
                                 fontsize=9, color=plan_colors[i])

    def generate_pdf_report(self, output_file="reporte_membresias.pdf"):
        """Genera el reporte PDF completo"""

        print("Generando reporte PDF...")

        with PdfPages(output_file) as pdf:
            # Página 1: Resumen Ejecutivo
            fig = plt.figure(figsize=(11.7, 8.3))  # A4 landscape
            fig.suptitle('REPORTE DE MEMBRESÍAS - RESUMEN EJECUTIVO\nMayo - Julio 2024',
                         fontsize=20, fontweight='bold', y=0.95)

            # Crear texto de resumen
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

            plt.text(0.05, 0.85, summary_text, fontsize=12, fontfamily='serif',
                     verticalalignment='top', transform=fig.transFigure,
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.5))

            plt.axis('off')
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 2: Comparación Mensual
            fig, axes = plt.subplots(2, 2, figsize=(11.7, 8.3))
            fig.suptitle('ANÁLISIS COMPARATIVO MENSUAL',
                         fontsize=18, fontweight='bold')
            self.plot_monthly_comparison(fig, axes)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 3: Análisis por Planes
            fig, axes = plt.subplots(2, 2, figsize=(11.7, 8.3))
            fig.suptitle('ANÁLISIS POR PLANES DE MEMBRESÍA',
                         fontsize=18, fontweight='bold')
            self.plot_plan_analysis(fig, axes)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 4: Análisis de Crecimiento - Vista General
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('ANALISIS DE CRECIMIENTO - VISTA GENERAL',
                         fontsize=18, fontweight='bold')
            self.create_growth_overview_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 5: Análisis de Crecimiento - Detalle Mensual
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('ANALISIS DE CRECIMIENTO - DETALLE MENSUAL',
                         fontsize=18, fontweight='bold')
            self.create_monthly_growth_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 6: Análisis de Crecimiento - Por Planes
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('ANALISIS DE CRECIMIENTO - POR PLANES',
                         fontsize=18, fontweight='bold')
            self.create_plan_growth_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            # Página 7: Datos Detallados
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('DATOS DETALLADOS POR MES',
                         fontsize=18, fontweight='bold')

            # Tabla de resumen mensual
            table_data = self.monthly_summary.copy()
            table_data['ingresos_total'] = table_data['ingresos_total'].apply(
                lambda x: f'S/ {x:,.0f}')
            table_data['ticket_promedio'] = table_data['ticket_promedio'].apply(
                lambda x: f'S/ {x:,.0f}')

            ax = fig.add_subplot(111)
            ax.axis('tight')
            ax.axis('off')

            table = ax.table(cellText=table_data.values,
                             colLabels=['Mes', 'Orden', 'Ingresos Totales', 'Ticket Promedio',
                                        'Total Membresías', 'Clientes Únicos'],
                             cellLoc='center', loc='center',
                             bbox=[0.1, 0.3, 0.8, 0.4])

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)

            # Tabla de planes
            plan_table_data = self.stats['by_plan'].copy()
            plan_table_data['ingresos'] = plan_table_data['ingresos'].apply(
                lambda x: f'S/ {x:,.0f}')
            plan_table_data['ticket_promedio'] = plan_table_data['ticket_promedio'].apply(
                lambda x: f'S/ {x:,.0f}')

            table2 = ax.table(cellText=plan_table_data.values,
                              colLabels=['Ingresos', 'Cantidad',
                                         'Ticket Promedio', 'Clientes Únicos'],
                              rowLabels=plan_table_data.index,
                              cellLoc='center', loc='center',
                              bbox=[0.1, 0.05, 0.8, 0.2])

            table2.auto_set_font_size(False)
            table2.set_fontsize(9)
            table2.scale(1, 1.5)

            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

        print(f"Reporte generado exitosamente: {output_file}")

    def run_analysis(self, output_file="reporte_membresias.pdf"):
        """Ejecuta el análisis completo"""
        print("Iniciando analisis de membresias...")

        self.load_data()
        self.prepare_data()
        self.create_summary_stats()
        self.generate_pdf_report(output_file)

        print("Analisis completado!")

# Función principal


def main():
    """Función principal para ejecutar el generador de reportes"""

    # Crear instancia del generador
    generator = MembershipReportGenerator()

    # Ejecutar análisis
    generator.run_analysis("reporte_membresias_completo.pdf")

    print("\n" + "="*50)
    print("REPORTE GENERADO EXITOSAMENTE")
    print("="*50)
    print("Archivo: reporte_membresias_completo.pdf")
    print("Paginas: 7 paginas con analisis completo")
    print("Incluye: Metricas, graficos y tablas detalladas")
    print("\nESTRUCTURA DEL REPORTE:")
    print("1. Resumen Ejecutivo")
    print("2. Comparacion Mensual")
    print("3. Analisis por Planes")
    print("4. Crecimiento - Vista General")
    print("5. Crecimiento - Detalle Mensual")
    print("6. Crecimiento - Por Planes")
    print("7. Datos Detallados")


if __name__ == "__main__":
    # Instalar dependencias necesarias
    print("Verificando dependencias...")
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("Todas las dependencias estan instaladas")
    except ImportError as e:
        print(f"Falta instalar: {e}")
        print("Ejecuta: pip install pandas matplotlib seaborn")
        exit(1)

    main()
