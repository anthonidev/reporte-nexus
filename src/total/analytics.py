"""
Módulo para análisis y cálculos estadísticos de pagos totales
"""

import pandas as pd
import numpy as np


class TotalAnalytics:
    """Maneja todos los cálculos y análisis estadísticos para pagos totales"""

    def __init__(self, combined_df, monthly_summary, monthly_category_summary):
        self.combined_df = combined_df
        self.monthly_summary = monthly_summary
        self.monthly_category_summary = monthly_category_summary
        self.stats = {}

    def calculate_all_stats(self):
        """Calcula todas las estadísticas necesarias"""
        self._calculate_general_stats()
        self._calculate_category_stats()
        self._calculate_growth_rates()
        self._calculate_category_growth()
        self._calculate_trends()
        self._calculate_projections()
        self._calculate_diversity_metrics()
        return self.stats

    def _calculate_general_stats(self):
        """Calcula estadísticas generales"""
        self.stats['total_revenue'] = self.combined_df['amount'].sum()
        self.stats['total_transactions'] = len(self.combined_df)
        self.stats['unique_customers'] = self.combined_df['email'].nunique()
        self.stats['avg_ticket'] = self.combined_df['amount'].mean()

        # Estadísticas adicionales
        self.stats['median_ticket'] = self.combined_df['amount'].median()
        self.stats['min_transaction'] = self.combined_df['amount'].min()
        self.stats['max_transaction'] = self.combined_df['amount'].max()
        self.stats['std_ticket'] = self.combined_df['amount'].std()

    def _calculate_category_stats(self):
        """Calcula estadísticas por categoría"""
        category_stats = self.combined_df.groupby('category_clean').agg({
            'amount': ['sum', 'count', 'mean', 'median'],
            'email': 'nunique'
        }).round(2)

        category_stats.columns = [
            'ingresos', 'cantidad', 'ticket_promedio', 'ticket_mediano', 'clientes_únicos'
        ]
        self.stats['by_category'] = category_stats.sort_values(
            'ingresos', ascending=False)

        # Participación porcentual de cada categoría
        total_revenue = self.stats['total_revenue']
        self.stats['category_participation'] = (
            (category_stats['ingresos'] / total_revenue * 100).round(1)
        )

    def _calculate_growth_rates(self):
        """Calcula tasas de crecimiento mensual"""
        monthly_revenue = self.monthly_summary.set_index('month')[
            'ingresos_total']
        monthly_transactions = self.monthly_summary.set_index('month')[
            'total_transacciones']
        monthly_tickets = self.monthly_summary.set_index('month')[
            'ticket_promedio']
        monthly_customers = self.monthly_summary.set_index('month')[
            'clientes_únicos']

        # Tasas de crecimiento porcentual
        self.stats['growth_rates'] = {
            'ingresos': monthly_revenue.pct_change().fillna(0) * 100,
            'transacciones': monthly_transactions.pct_change().fillna(0) * 100,
            'ticket_promedio': monthly_tickets.pct_change().fillna(0) * 100,
            'clientes_unicos': monthly_customers.pct_change().fillna(0) * 100
        }

        # Cambios absolutos
        self.stats['absolute_changes'] = {
            'ingresos': monthly_revenue.diff().fillna(0),
            'transacciones': monthly_transactions.diff().fillna(0),
            'ticket_promedio': monthly_tickets.diff().fillna(0),
            'clientes_unicos': monthly_customers.diff().fillna(0)
        }

    def _calculate_category_growth(self):
        """Calcula el crecimiento por categorías"""
        category_growth = {}

        for category in self.combined_df['category_clean'].unique():
            cat_data = self.monthly_category_summary[
                self.monthly_category_summary['category_clean'] == category
            ]

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

        self.stats['category_growth'] = category_growth

    def _calculate_trends(self):
        """Calcula tendencias y patrones"""
        monthly_revenue = self.monthly_summary.set_index('month')[
            'ingresos_total']
        monthly_transactions = self.monthly_summary.set_index('month')[
            'total_transacciones']

        self.stats['trends'] = {
            'mejor_mes_ingresos': monthly_revenue.idxmax(),
            'peor_mes_ingresos': monthly_revenue.idxmin(),
            'mejor_mes_transacciones': monthly_transactions.idxmax(),
            'mejor_categoria': self.stats['by_category'].index[0],
            'categoria_mas_crecimiento': self._get_best_growing_category(),
            'promedio_crecimiento_ingresos': self.stats['growth_rates']['ingresos'].mean(),
            'promedio_crecimiento_transacciones': self.stats['growth_rates']['transacciones'].mean()
        }

        # Análisis de estacionalidad
        self._analyze_seasonality()

    def _get_best_growing_category(self):
        """Identifica la categoría con mejor crecimiento promedio"""
        best_growth = -float('inf')
        best_category = 'N/A'

        for category, data in self.stats['category_growth'].items():
            if len(data['revenue_growth']) > 0:
                avg_growth = data['revenue_growth'].mean()
                if avg_growth > best_growth:
                    best_growth = avg_growth
                    best_category = category

        return best_category

    def _analyze_seasonality(self):
        """Analiza patrones estacionales"""
        monthly_data = self.monthly_summary.set_index('month')[
            'ingresos_total']

        # Calcular variabilidad
        cv = (monthly_data.std() / monthly_data.mean()) * 100

        # Determinar estacionalidad
        if cv > 20:
            seasonality = "Alta variabilidad"
        elif cv > 10:
            seasonality = "Moderada variabilidad"
        else:
            seasonality = "Baja variabilidad"

        self.stats['seasonality'] = {
            'coefficient_variation': cv,
            'pattern': seasonality,
            'peak_month': monthly_data.idxmax(),
            'low_month': monthly_data.idxmin()
        }

    def _calculate_projections(self):
        """Calcula proyecciones para el siguiente mes"""
        monthly_revenue = self.monthly_summary.set_index('month')[
            'ingresos_total']
        monthly_transactions = self.monthly_summary.set_index('month')[
            'total_transacciones']

        if len(monthly_revenue) >= 2:
            # Proyección simple basada en tendencia lineal
            revenue_trend = monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2]
            transaction_trend = monthly_transactions.iloc[-1] - \
                monthly_transactions.iloc[-2]

            # Proyección basada en promedio móvil
            if len(monthly_revenue) >= 3:
                revenue_ma = monthly_revenue.rolling(window=2).mean().iloc[-1]
                transaction_ma = monthly_transactions.rolling(
                    window=2).mean().iloc[-1]
            else:
                revenue_ma = monthly_revenue.mean()
                transaction_ma = monthly_transactions.mean()

            self.stats['projections'] = {
                'agosto_ingresos_estimados': monthly_revenue.iloc[-1] + revenue_trend,
                'agosto_transacciones_estimadas': monthly_transactions.iloc[-1] + transaction_trend,
                'agosto_ingresos_ma': revenue_ma,
                'agosto_transacciones_ma': transaction_ma,
                'tendencia_ingresos': 'Creciente' if revenue_trend > 0 else 'Decreciente',
                'tendencia_transacciones': 'Creciente' if transaction_trend > 0 else 'Decreciente',
                'confianza_proyeccion': self._calculate_projection_confidence()
            }

    def _calculate_projection_confidence(self):
        """Calcula nivel de confianza de las proyecciones"""
        growth_rates = self.stats['growth_rates']['ingresos']
        volatility = growth_rates.std()

        if volatility < 10:
            return "Alta"
        elif volatility < 25:
            return "Media"
        else:
            return "Baja"

    def _calculate_diversity_metrics(self):
        """Calcula métricas de diversificación del negocio"""
        category_revenues = self.stats['by_category']['ingresos']
        total_revenue = category_revenues.sum()

        # Índice Herfindahl-Hirschman (concentración)
        market_shares = category_revenues / total_revenue
        hhi = (market_shares ** 2).sum()

        # Entropía de Shannon (diversidad)
        shannon_entropy = - \
            (market_shares * np.log2(market_shares + 1e-10)).sum()

        # Interpretación de concentración
        if hhi > 0.5:
            concentration_level = "Alta concentración"
        elif hhi > 0.25:
            concentration_level = "Concentración moderada"
        else:
            concentration_level = "Baja concentración"

        self.stats['diversity'] = {
            'hhi_index': hhi,
            'shannon_entropy': shannon_entropy,
            'concentration_level': concentration_level,
            'dominant_category_share': market_shares.max(),
            'category_count': len(category_revenues)
        }

    def get_executive_summary_data(self):
        """Retorna datos para el resumen ejecutivo"""
        total_growth_revenue = (
            (self.monthly_summary['ingresos_total'].iloc[-1] -
             self.monthly_summary['ingresos_total'].iloc[0]) /
            self.monthly_summary['ingresos_total'].iloc[0]
        ) * 100 if len(self.monthly_summary) > 1 else 0

        return {
            'total_revenue': self.stats['total_revenue'],
            'total_transactions': self.stats['total_transactions'],
            'unique_customers': self.stats['unique_customers'],
            'avg_ticket': self.stats['avg_ticket'],
            'total_growth': total_growth_revenue,
            'best_month': self.stats['trends']['mejor_mes_ingresos'],
            'best_category': self.stats['trends']['mejor_categoria'],
            'august_projection': self.stats['projections']['agosto_ingresos_estimados'],
            'business_concentration': self.stats['diversity']['concentration_level']
        }

    def get_category_performance_ranking(self):
        """Retorna ranking de rendimiento por categorías"""
        categories = self.stats['by_category'].copy()

        # Agregar métricas adicionales
        categories['participacion'] = self.stats['category_participation']

        # Calcular score de rendimiento
        categories['performance_score'] = (
            categories['ingresos'] / categories['ingresos'].max() * 0.4 +
            categories['cantidad'] / categories['cantidad'].max() * 0.3 +
            categories['ticket_promedio'] /
            categories['ticket_promedio'].max() * 0.3
        )

        return categories.sort_values('performance_score', ascending=False)

    def detect_anomalies(self):
        """Detecta anomalías en los datos"""
        anomalies = []

        # Detectar transacciones atípicas
        Q1 = self.combined_df['amount'].quantile(0.25)
        Q3 = self.combined_df['amount'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = self.combined_df[
            (self.combined_df['amount'] < lower_bound) |
            (self.combined_df['amount'] > upper_bound)
        ]

        if len(outliers) > 0:
            anomalies.append(
                f"Se encontraron {len(outliers)} transacciones atípicas")

        # Detectar caídas significativas mes a mes
        for metric in ['ingresos', 'transacciones']:
            growth_rates = self.stats['growth_rates'][metric]
            significant_drops = growth_rates[growth_rates < -20]

            if len(significant_drops) > 0:
                anomalies.append(
                    f"Caída significativa en {metric}: {significant_drops.to_dict()}")

        return anomalies
