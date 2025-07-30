#!/usr/bin/env python3
"""
Generador de Reporte PDF - Análisis Total de Pagos
Analiza todos los pagos (membresías, productos, reconsumos, upgrades) de mayo, junio y julio 2024
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


class TotalPaymentsReportGenerator:
    def __init__(self, data_path="data/total/"):
        self.data_path = data_path
        self.months = ['mayo', 'junio', 'julio']
        self.month_names = {'mayo': 'Mayo', 'junio': 'Junio', 'julio': 'Julio'}
        self.category_names = {
            'membership': 'Membresías',
            'order': 'Productos',
            'membership_reconsumption': 'Reconsumo',
            'membership_upgrade': 'Upgrade'
        }
        self.dfs = {}

    def load_data(self):
        """Carga los datos de los 3 meses"""
        for month in self.months:
            file_path = f"{self.data_path}total-{month}.csv"
            try:
                df = pd.read_csv(file_path)
                df['month'] = self.month_names[month]
                df['month_order'] = self.months.index(month) + 1
                # Limpiar categorías
                df['category_clean'] = df['relatedEntityType'].map(
                    self.category_names).fillna(df['relatedEntityType'])
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
        self.combined_df['amount'] = pd.to_numeric(
            self.combined_df['amount'], errors='coerce')
        self.combined_df = self.combined_df.dropna(subset=['amount'])

        # Crear resumen por mes y categoría
        self.monthly_category_summary = self.combined_df.groupby(['month', 'month_order', 'category_clean']).agg({
            'amount': ['sum', 'mean', 'count'],
            'email': 'nunique'
        }).round(2)

        self.monthly_category_summary.columns = [
            'ingresos_total', 'ticket_promedio', 'total_transacciones', 'clientes_únicos']
        self.monthly_category_summary = self.monthly_category_summary.reset_index()

        # Resumen por mes (total)
        self.monthly_summary = self.combined_df.groupby(['month', 'month_order']).agg({
            'amount': ['sum', 'mean', 'count'],
            'email': 'nunique'
        }).round(2)

        self.monthly_summary.columns = [
            'ingresos_total', 'ticket_promedio', 'total_transacciones', 'clientes_únicos']
        self.monthly_summary = self.monthly_summary.reset_index().sort_values('month_order')

    def create_summary_stats(self):
        """Genera estadísticas de resumen"""
        stats = {}

        # Estadísticas generales
        stats['total_revenue'] = self.combined_df['amount'].sum()
        stats['total_transactions'] = len(self.combined_df)
        stats['unique_customers'] = self.combined_df['email'].nunique()
        stats['avg_ticket'] = self.combined_df['amount'].mean()

        # Por categoría
        category_stats = self.combined_df.groupby('category_clean').agg({
            'amount': ['sum', 'count', 'mean'],
            'email': 'nunique'
        }).round(2)
        category_stats.columns = [
            'ingresos', 'cantidad', 'ticket_promedio', 'clientes_únicos']
        stats['by_category'] = category_stats.sort_values(
            'ingresos', ascending=False)

        # Crecimiento mensual por categoría
        category_growth = {}
        for category in self.combined_df['category_clean'].unique():
            cat_data = self.monthly_category_summary[self.monthly_category_summary['category_clean'] == category]
            if len(cat_data) > 1:
                cat_data_sorted = cat_data.sort_values('month_order')
                revenue_growth = cat_data_sorted.set_index(
                    'month')['ingresos_total'].pct_change().fillna(0) * 100
                count_growth = cat_data_sorted.set_index(
                    'month')['total_transacciones'].pct_change().fillna(0) * 100
                category_growth[category] = {
                    'revenue_growth': revenue_growth,
                    'count_growth': count_growth
                }

        stats['category_growth'] = category_growth

        # Crecimiento general mensual
        monthly_revenue = self.monthly_summary.set_index('month')[
            'ingresos_total']
        monthly_transactions = self.monthly_summary.set_index('month')[
            'total_transacciones']
        monthly_customers = self.monthly_summary.set_index('month')[
            'clientes_únicos']

        stats['growth_rates'] = {
            'ingresos': monthly_revenue.pct_change().fillna(0) * 100,
            'transacciones': monthly_transactions.pct_change().fillna(0) * 100,
            'clientes_unicos': monthly_customers.pct_change().fillna(0) * 100
        }

        # Cambios absolutos
        stats['absolute_changes'] = {
            'ingresos': monthly_revenue.diff().fillna(0),
            'transacciones': monthly_transactions.diff().fillna(0),
            'clientes_unicos': monthly_customers.diff().fillna(0)
        }

        # Análisis de tendencias
        stats['trends'] = {
            'mejor_mes_ingresos': monthly_revenue.idxmax(),
            'peor_mes_ingresos': monthly_revenue.idxmin(),
            'mejor_categoria': stats['by_category'].index[0],
            'categoria_mas_crecimiento': self._get_best_growing_category(category_growth),
            'promedio_crecimiento_ingresos': stats['growth_rates']['ingresos'].mean()
        }

        # Proyecciones simples
        if len(monthly_revenue) >= 2:
            revenue_trend = (
                monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2])
            transaction_trend = (
                monthly_transactions.iloc[-1] - monthly_transactions.iloc[-2])

            stats['projections'] = {
                'agosto_ingresos_estimados': monthly_revenue.iloc[-1] + revenue_trend,
                'agosto_transacciones_estimadas': monthly_transactions.iloc[-1] + transaction_trend,
                'tendencia_ingresos': 'Creciente' if revenue_trend > 0 else 'Decreciente',
                'tendencia_transacciones': 'Creciente' if transaction_trend > 0 else 'Decreciente'
            }

        self.stats = stats

    def _get_best_growing_category(self, category_growth):
        """Encuentra la categoría con mayor crecimiento promedio"""
        best_growth = -float('inf')
        best_category = 'N/A'

        for category, data in category_growth.items():
            if len(data['revenue_growth']) > 0:
                avg_growth = data['revenue_growth'].mean()
                if avg_growth > best_growth:
                    best_growth = avg_growth
                    best_category = category

        return best_category

    def create_executive_summary_page(self, fig):
        """Página de resumen ejecutivo"""

        # Crear layout
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. Gráfico de ingresos totales por mes
        ax1 = fig.add_subplot(gs[0, 0])
        months = self.monthly_summary['month'].tolist()
        revenue = self.monthly_summary['ingresos_total'].tolist()

        bars = ax1.bar(months, revenue, color=[
                       '#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8)
        ax1.set_title('INGRESOS TOTALES POR MES',
                      fontsize=14, fontweight='bold')
        ax1.set_ylabel('Ingresos (S/)', fontsize=12, fontweight='bold')

        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                     f'S/ {height:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

        ax1.grid(True, alpha=0.3)

        # 2. Distribución por categorías (pie chart)
        ax2 = fig.add_subplot(gs[0, 1])
        category_totals = self.stats['by_category']['ingresos']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

        wedges, texts, autotexts = ax2.pie(category_totals.values, labels=category_totals.index,
                                           autopct='%1.1f%%', colors=colors[:len(category_totals)],
                                           startangle=90)
        ax2.set_title('DISTRIBUCION POR CATEGORIAS',
                      fontsize=14, fontweight='bold')

        # 3. Resumen de métricas clave
        ax3 = fig.add_subplot(gs[1, :])
        ax3.axis('off')

        # Calcular crecimiento total
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

        ax3.text(0.02, 0.98, summary_text, fontsize=11, fontweight='bold',
                 verticalalignment='top', transform=ax3.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f8ff", alpha=0.9))

    def create_monthly_comparison_page(self, fig):
        """Página de comparación mensual"""

        # Crear grid de 2x2
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

        # 1. Ingresos por mes
        ax1 = fig.add_subplot(gs[0, 0])
        months = self.monthly_summary['month'].tolist()
        revenue = self.monthly_summary['ingresos_total'].tolist()

        bars1 = ax1.bar(months, revenue, color=[
                        '#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax1.set_title('Ingresos por Mes', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Ingresos (S/)', fontsize=12)

        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                     f'S/ {height:,.0f}', ha='center', va='bottom', fontweight='bold')

        # 2. Número de transacciones por mes
        ax2 = fig.add_subplot(gs[0, 1])
        transactions = self.monthly_summary['total_transacciones'].tolist()

        bars2 = ax2.bar(months, transactions, color=[
                        '#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax2.set_title('Transacciones por Mes', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Cantidad', fontsize=12)

        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                     f'{int(height)}', ha='center', va='bottom', fontweight='bold')

        # 3. Ticket promedio por mes
        ax3 = fig.add_subplot(gs[1, 0])
        tickets = self.monthly_summary['ticket_promedio'].tolist()

        bars3 = ax3.bar(months, tickets, color=[
                        '#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax3.set_title('Ticket Promedio por Mes',
                      fontsize=14, fontweight='bold')
        ax3.set_ylabel('Ticket Promedio (S/)', fontsize=12)

        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                     f'S/ {height:,.0f}', ha='center', va='bottom', fontweight='bold')

        # 4. Evolución de ingresos por categoría
        ax4 = fig.add_subplot(gs[1, 1])

        # Preparar datos para gráfico de líneas
        category_evolution = self.combined_df.groupby(['month', 'category_clean'])[
            'amount'].sum().unstack(fill_value=0)
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

        for i, category in enumerate(category_evolution.columns):
            ax4.plot(category_evolution.index, category_evolution[category],
                     marker='o', linewidth=3, markersize=8, label=category, color=colors[i])

        ax4.set_title('Evolución por Categoría',
                      fontsize=14, fontweight='bold')
        ax4.set_ylabel('Ingresos (S/)', fontsize=12)
        ax4.legend(fontsize=10, loc='upper left')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

    def create_category_analysis_page(self, fig):
        """Página de análisis por categorías"""

        # Crear grid de 2x3
        gs = fig.add_gridspec(2, 3, hspace=0.4, wspace=0.3)

        # 1. Ingresos por categoría (horizontal bar)
        ax1 = fig.add_subplot(gs[0, 0])
        category_revenue = self.stats['by_category']['ingresos'].sort_values(
            ascending=True)
        colors = ['#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']

        bars1 = ax1.barh(category_revenue.index, category_revenue.values,
                         color=colors[:len(category_revenue)])
        ax1.set_title('Ingresos por Categoría', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Ingresos (S/)', fontsize=10)

        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                     f'S/ {width:,.0f}', ha='left', va='center', fontweight='bold', fontsize=9)

        # 2. Cantidad por categoría
        ax2 = fig.add_subplot(gs[0, 1])
        category_count = self.stats['by_category']['cantidad'].sort_values(
            ascending=True)

        bars2 = ax2.barh(category_count.index, category_count.values,
                         color=colors[:len(category_count)])
        ax2.set_title('Cantidad por Categoría', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Cantidad', fontsize=10)

        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                     f'{int(width)}', ha='left', va='center', fontweight='bold', fontsize=9)

        # 3. Ticket promedio por categoría
        ax3 = fig.add_subplot(gs[0, 2])
        category_ticket = self.stats['by_category']['ticket_promedio'].sort_values(
            ascending=True)

        bars3 = ax3.barh(category_ticket.index, category_ticket.values,
                         color=colors[:len(category_ticket)])
        ax3.set_title('Ticket Promedio', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Ticket (S/)', fontsize=10)

        for i, bar in enumerate(bars3):
            width = bar.get_width()
            ax3.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                     f'S/ {width:,.0f}', ha='left', va='center', fontweight='bold', fontsize=9)

        # 4. Matriz de categorías por mes (heatmap)
        ax4 = fig.add_subplot(gs[1, :])

        # Preparar datos para heatmap
        heatmap_data = self.combined_df.groupby(['month', 'category_clean'])[
            'amount'].sum().unstack(fill_value=0)

        im = ax4.imshow(heatmap_data.T.values, cmap='YlOrRd', aspect='auto')
        ax4.set_xticks(range(len(heatmap_data.index)))
        ax4.set_xticklabels(heatmap_data.index)
        ax4.set_yticks(range(len(heatmap_data.columns)))
        ax4.set_yticklabels(heatmap_data.columns)
        ax4.set_title('MAPA DE CALOR - INGRESOS POR CATEGORIA Y MES',
                      fontsize=14, fontweight='bold', pad=20)

        # Agregar valores en el heatmap
        for i in range(len(heatmap_data.columns)):
            for j in range(len(heatmap_data.index)):
                value = heatmap_data.iloc[j, i]
                ax4.text(j, i, f'S/ {value:,.0f}', ha='center', va='center',
                         fontweight='bold', fontsize=10, color='white' if value > heatmap_data.values.max()*0.5 else 'black')

        # Colorbar
        cbar = plt.colorbar(
            im, ax=ax4, orientation='horizontal', pad=0.1, shrink=0.8)
        cbar.set_label('Ingresos (S/)', fontweight='bold')

    def create_growth_overview_page(self, fig):
        """Página de análisis de crecimiento general"""

        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. Evolución de ingresos y transacciones
        ax1 = fig.add_subplot(gs[0, :])
        months = self.monthly_summary['month'].tolist()
        revenue = self.monthly_summary['ingresos_total'].tolist()
        transactions = self.monthly_summary['total_transacciones'].tolist()

        ax1_twin = ax1.twinx()

        line1 = ax1.plot(months, revenue, color='#FF6B6B', marker='o', linewidth=4,
                         markersize=12, label='Ingresos (S/)')
        ax1.set_ylabel('Ingresos (S/)', color='#FF6B6B',
                       fontsize=14, fontweight='bold')
        ax1.tick_params(axis='y', labelcolor='#FF6B6B', labelsize=12)

        line2 = ax1_twin.plot(months, transactions, color='#4ECDC4', marker='s', linewidth=4,
                              markersize=12, label='Transacciones')
        ax1_twin.set_ylabel('Número de Transacciones',
                            color='#4ECDC4', fontsize=14, fontweight='bold')
        ax1_twin.tick_params(axis='y', labelcolor='#4ECDC4', labelsize=12)

        ax1.set_title('EVOLUCION MENSUAL - INGRESOS Y TRANSACCIONES',
                      fontsize=16, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3)

        # Agregar valores
        for i, (month, rev, trans) in enumerate(zip(months, revenue, transactions)):
            ax1.annotate(f'S/ {rev:,.0f}', (i, rev), textcoords="offset points",
                         xytext=(0, 20), ha='center', fontweight='bold', color='#FF6B6B', fontsize=12)
            ax1_twin.annotate(f'{trans}', (i, trans), textcoords="offset points",
                              xytext=(0, -25), ha='center', fontweight='bold', color='#4ECDC4', fontsize=12)

        # 2. Resumen de crecimiento
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.axis('off')

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

        ax2.text(0.05, 0.95, growth_text, fontsize=12, fontweight='bold',
                 verticalalignment='top', transform=ax2.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f4fd", alpha=0.9))

        # 3. Proyecciones
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.axis('off')

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

        ax3.text(0.05, 0.95, projection_text, fontsize=12, fontweight='bold',
                 verticalalignment='top', transform=ax3.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff2e8", alpha=0.9))

    def create_monthly_growth_detail_page(self, fig):
        """Página de detalle de crecimiento mensual"""

        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

        # 1. Tasas de crecimiento porcentual
        ax1 = fig.add_subplot(gs[0, 0])
        growth_data = {
            'Ingresos': [self.stats['growth_rates']['ingresos']['Junio'],
                         self.stats['growth_rates']['ingresos']['Julio']],
            'Transacciones': [self.stats['growth_rates']['transacciones']['Junio'],
                              self.stats['growth_rates']['transacciones']['Julio']]
        }

        x_pos = np.arange(len(['Jun vs May', 'Jul vs Jun']))
        width = 0.35

        bars1 = ax1.bar(x_pos - width/2, growth_data['Ingresos'], width,
                        label='Ingresos', color='#FF6B6B', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, growth_data['Transacciones'], width,
                        label='Transacciones', color='#4ECDC4', alpha=0.8)

        ax1.set_ylabel('Crecimiento (%)', fontsize=12, fontweight='bold')
        ax1.set_title('TASAS DE CRECIMIENTO', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(['Jun vs May', 'Jul vs Jun'], fontsize=11)
        ax1.legend(fontsize=11)
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.grid(True, alpha=0.3)

        # Agregar valores
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3 if height >= 0 else -15), textcoords="offset points",
                             ha='center', va='bottom' if height >= 0 else 'top',
                             fontweight='bold', fontsize=10)

        # 2. Cambios absolutos
        ax2 = fig.add_subplot(gs[0, 1])
        revenue_changes = [
            self.stats['absolute_changes']['ingresos']['Junio'],
            self.stats['absolute_changes']['ingresos']['Julio']
        ]
        colors = ['green' if x >= 0 else 'red' for x in revenue_changes]

        bars2 = ax2.bar(['Jun vs May', 'Jul vs Jun'],
                        revenue_changes, color=colors, alpha=0.7)
        ax2.set_ylabel('Cambio Absoluto (S/)', fontsize=12, fontweight='bold')
        ax2.set_title('CAMBIO EN INGRESOS', fontsize=14, fontweight='bold')
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

        ax3.plot(months, tickets, color='#45B7D1',
                 marker='D', linewidth=4, markersize=10)
        ax3.set_ylabel('Ticket Promedio (S/)', fontsize=12, fontweight='bold')
        ax3.set_title('EVOLUCION TICKET PROMEDIO',
                      fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)

        for i, (month, ticket) in enumerate(zip(months, tickets)):
            ax3.annotate(f'S/ {ticket:,.0f}', (i, ticket), textcoords="offset points",
                         xytext=(0, 15), ha='center', fontweight='bold', fontsize=11)

        # 4. Panel de detalles
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')

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

        ax4.text(0.05, 0.95, details_text, fontsize=11, fontweight='bold',
                 verticalalignment='top', transform=ax4.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f8e8", alpha=0.9))

    def create_category_growth_page(self, fig):
        """Página de crecimiento por categorías"""

        gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3)

        # 1. Crecimiento de ingresos por categoría (Julio vs Junio)
        ax1 = fig.add_subplot(gs[0, 0])
        category_names = []
        category_growth_jul = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

        for category, data in self.stats['category_growth'].items():
            if 'Julio' in data['revenue_growth'].index:
                category_names.append(category)
                category_growth_jul.append(data['revenue_growth']['Julio'])

        if category_names:
            bars1 = ax1.bar(category_names, category_growth_jul,
                            color=colors[:len(category_names)], alpha=0.8)
            ax1.set_ylabel('Crecimiento (%)', fontsize=12, fontweight='bold')
            ax1.set_title('CRECIMIENTO INGRESOS\n(Julio vs Junio)',
                          fontsize=12, fontweight='bold')
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax1.grid(True, alpha=0.3)
            plt.setp(ax1.get_xticklabels(), rotation=45,
                     ha='right', fontsize=10)

            for bar in bars1:
                height = bar.get_height()
                ax1.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3 if height >= 0 else -15), textcoords="offset points",
                             ha='center', va='bottom' if height >= 0 else 'top',
                             fontweight='bold', fontsize=9)

        # 2. Crecimiento de cantidad por categoría
        ax2 = fig.add_subplot(gs[0, 1])
        category_count_growth = []

        for category in category_names:
            if category in self.stats['category_growth'] and 'Julio' in self.stats['category_growth'][category]['count_growth'].index:
                category_count_growth.append(
                    self.stats['category_growth'][category]['count_growth']['Julio'])
            else:
                category_count_growth.append(0)

        if category_names:
            bars2 = ax2.bar(category_names, category_count_growth,
                            color=colors[:len(category_names)], alpha=0.8)
            ax2.set_ylabel('Crecimiento (%)', fontsize=12, fontweight='bold')
            ax2.set_title('CRECIMIENTO CANTIDAD\n(Julio vs Junio)',
                          fontsize=12, fontweight='bold')
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.get_xticklabels(), rotation=45,
                     ha='right', fontsize=10)

            for bar in bars2:
                height = bar.get_height()
                ax2.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3 if height >= 0 else -15), textcoords="offset points",
                             ha='center', va='bottom' if height >= 0 else 'top',
                             fontweight='bold', fontsize=9)

        # 3. Evolución temporal completa por categoría
        ax3 = fig.add_subplot(gs[1, :])
        category_evolution = self.combined_df.groupby(['month', 'category_clean'])[
            'amount'].sum().unstack(fill_value=0)

        for i, category in enumerate(category_evolution.columns):
            ax3.plot(category_evolution.index, category_evolution[category],
                     marker='o', linewidth=3, markersize=8, label=category, color=colors[i])

        ax3.set_title('EVOLUCION DE INGRESOS POR CATEGORIA (Mayo - Julio)',
                      fontsize=14, fontweight='bold')
        ax3.set_ylabel('Ingresos (S/)', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=11, loc='upper left')
        ax3.grid(True, alpha=0.3)

        # Agregar valores en los puntos
        for i, category in enumerate(category_evolution.columns):
            for j, (month, value) in enumerate(zip(category_evolution.index, category_evolution[category])):
                if value > 0:
                    ax3.annotate(f'S/ {value:,.0f}', (j, value), textcoords="offset points",
                                 xytext=(0, 10 + i*15), ha='center', fontweight='bold',
                                 fontsize=9, color=colors[i])

        # 4. Análisis detallado por categoría
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')

        # Crear tabla resumen de crecimiento por categoría
        growth_summary = "RESUMEN DE CRECIMIENTO POR CATEGORIA:\n\n"

        for category, data in self.stats['category_growth'].items():
            if len(data['revenue_growth']) >= 2:
                may_jun = data['revenue_growth']['Junio'] if 'Junio' in data['revenue_growth'].index else 0
                jun_jul = data['revenue_growth']['Julio'] if 'Julio' in data['revenue_growth'].index else 0
                growth_summary += f"{category.upper()}:\n"
                growth_summary += f"  • Mayo → Junio: {may_jun:+.1f}%\n"
                growth_summary += f"  • Junio → Julio: {jun_jul:+.1f}%\n\n"

        ax4.text(0.02, 0.98, growth_summary, fontsize=11, fontweight='bold',
                 verticalalignment='top', transform=ax4.transAxes,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f8f8", alpha=0.9))

    def create_detailed_tables_page(self, fig):
        """Página con tablas detalladas"""

        fig.suptitle('DATOS DETALLADOS - RESUMEN COMPLETO',
                     fontsize=18, fontweight='bold')

        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')

        # Tabla 1: Resumen mensual
        table_data_monthly = self.monthly_summary.copy()
        table_data_monthly['ingresos_total'] = table_data_monthly['ingresos_total'].apply(
            lambda x: f'S/ {x:,.0f}')
        table_data_monthly['ticket_promedio'] = table_data_monthly['ticket_promedio'].apply(
            lambda x: f'S/ {x:,.0f}')

        table1 = ax.table(cellText=table_data_monthly.values,
                          colLabels=['Mes', 'Orden', 'Ingresos Totales', 'Ticket Promedio',
                                     'Total Transacciones', 'Clientes Únicos'],
                          cellLoc='center', loc='center',
                          bbox=[0.05, 0.7, 0.9, 0.25])

        table1.auto_set_font_size(False)
        table1.set_fontsize(10)
        table1.scale(1, 2)

        # Título para tabla mensual
        ax.text(0.5, 0.97, 'RESUMEN MENSUAL', ha='center', va='top',
                fontsize=14, fontweight='bold', transform=ax.transAxes)

        # Tabla 2: Resumen por categorías
        table_data_category = self.stats['by_category'].copy()
        table_data_category['ingresos'] = table_data_category['ingresos'].apply(
            lambda x: f'S/ {x:,.0f}')
        table_data_category['ticket_promedio'] = table_data_category['ticket_promedio'].apply(
            lambda x: f'S/ {x:,.0f}')

        table2 = ax.table(cellText=table_data_category.values,
                          colLabels=['Ingresos', 'Cantidad',
                                     'Ticket Promedio', 'Clientes Únicos'],
                          rowLabels=table_data_category.index,
                          cellLoc='center', loc='center',
                          bbox=[0.05, 0.35, 0.9, 0.25])

        table2.auto_set_font_size(False)
        table2.set_fontsize(10)
        table2.scale(1, 1.8)

        # Título para tabla de categorías
        ax.text(0.5, 0.62, 'RESUMEN POR CATEGORIAS', ha='center', va='top',
                fontsize=14, fontweight='bold', transform=ax.transAxes)

        # Resumen de insights clave
        insights_text = f"""
INSIGHTS CLAVE DEL ANALISIS:

• CATEGORIA MAS RENTABLE: {self.stats['trends']['mejor_categoria']} 
  (S/ {self.stats['by_category'].loc[self.stats['trends']['mejor_categoria'], 'ingresos']:,.0f})

• MAYOR CRECIMIENTO: {self.stats['trends']['categoria_mas_crecimiento']}

• MEJOR MES: {self.stats['trends']['mejor_mes_ingresos']} 
  (S/ {self.monthly_summary[self.monthly_summary['month'] == self.stats['trends']['mejor_mes_ingresos']]['ingresos_total'].iloc[0]:,.0f})

• PROYECCION AGOSTO: S/ {self.stats['projections']['agosto_ingresos_estimados']:,.0f}
  ({self.stats['projections']['tendencia_ingresos']})
        """

        ax.text(0.5, 0.3, insights_text, ha='center', va='top',
                fontsize=12, fontweight='bold', transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#e8f8f5", alpha=0.9))

    def generate_pdf_report(self, output_file="reporte_pagos_totales.pdf"):
        """Genera el reporte PDF completo"""

        print("Generando reporte PDF...")

        with PdfPages(output_file) as pdf:
            # Página 1: Resumen Ejecutivo
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('REPORTE TOTAL DE PAGOS - RESUMEN EJECUTIVO\nMayo - Julio 2024',
                         fontsize=20, fontweight='bold', y=0.95)
            self.create_executive_summary_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 2: Comparación Mensual
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('COMPARACION MENSUAL - TODAS LAS CATEGORIAS',
                         fontsize=18, fontweight='bold')
            self.create_monthly_comparison_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 3: Análisis por Categorías
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('ANALISIS DETALLADO POR CATEGORIAS',
                         fontsize=18, fontweight='bold')
            self.create_category_analysis_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 4: Crecimiento - Vista General
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('ANALISIS DE CRECIMIENTO - VISTA GENERAL',
                         fontsize=18, fontweight='bold')
            self.create_growth_overview_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 5: Crecimiento - Detalle Mensual
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('ANALISIS DE CRECIMIENTO - DETALLE MENSUAL',
                         fontsize=18, fontweight='bold')
            self.create_monthly_growth_detail_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 6: Crecimiento por Categorías
            fig = plt.figure(figsize=(11.7, 8.3))
            fig.suptitle('ANALISIS DE CRECIMIENTO - POR CATEGORIAS',
                         fontsize=18, fontweight='bold')
            self.create_category_growth_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            # Página 7: Tablas Detalladas
            fig = plt.figure(figsize=(11.7, 8.3))
            self.create_detailed_tables_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

        print(f"Reporte generado exitosamente: {output_file}")

    def run_analysis(self, output_file="reporte_pagos_totales.pdf"):
        """Ejecuta el análisis completo"""
        print("Iniciando analisis de pagos totales...")

        self.load_data()
        self.prepare_data()
        self.create_summary_stats()
        self.generate_pdf_report(output_file)

        print("Analisis completado!")

# Función principal


def main():
    """Función principal para ejecutar el generador de reportes"""

    # Crear instancia del generador
    generator = TotalPaymentsReportGenerator()

    # Ejecutar análisis
    generator.run_analysis("reporte_pagos_totales_completo.pdf")

    print("\n" + "="*60)
    print("REPORTE DE PAGOS TOTALES GENERADO EXITOSAMENTE")
    print("="*60)
    print("Archivo: reporte_pagos_totales_completo.pdf")
    print("Paginas: 7 paginas con analisis completo")
    print("Categorias: Membresias, Productos, Reconsumo, Upgrade")
    print("\nESTRUCTURA DEL REPORTE:")
    print("1. Resumen Ejecutivo")
    print("2. Comparacion Mensual")
    print("3. Analisis por Categorias")
    print("4. Crecimiento - Vista General")
    print("5. Crecimiento - Detalle Mensual")
    print("6. Crecimiento - Por Categorias")
    print("7. Datos Detallados")
    print("\nCATEGORIAS ANALIZADAS:")
    print("• Membresias (membership)")
    print("• Productos (order)")
    print("• Reconsumo (membership_reconsumption)")
    print("• Upgrade (membership_upgrade)")


if __name__ == "__main__":
    # Verificar dependencias
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
