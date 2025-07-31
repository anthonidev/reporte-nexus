import pandas as pd
import numpy as np


class MembershipAnalytics:

    def __init__(self, combined_df, monthly_summary):
        self.combined_df = combined_df
        self.monthly_summary = monthly_summary
        self.stats = {}

    def calculate_all_stats(self):
        """Calcula todas las estadísticas necesarias"""
        self._calculate_general_stats()
        self._calculate_plan_stats()
        self._calculate_growth_rates()
        self._calculate_trends()
        self._calculate_projections()
        return self.stats

    def _calculate_general_stats(self):
        """Calcula estadísticas generales"""
        self.stats['total_revenue'] = self.combined_df['amount'].sum()
        self.stats['total_memberships'] = len(self.combined_df)
        self.stats['unique_customers'] = self.combined_df['email'].nunique()
        self.stats['avg_ticket'] = self.combined_df['amount'].mean()

    def _calculate_plan_stats(self):
        """Calcula estadísticas por plan"""
        plan_stats = self.combined_df.groupby('membership_plan_name').agg({
            'amount': ['sum', 'count', 'mean'],
            'email': 'nunique'
        }).round(2)

        plan_stats.columns = ['ingresos', 'cantidad',
                              'ticket_promedio', 'clientes_únicos']
        self.stats['by_plan'] = plan_stats.sort_values(
            'ingresos', ascending=False)

    def _calculate_growth_rates(self):
        """Calcula tasas de crecimiento mensual"""
        monthly_revenue = self.monthly_summary.set_index('month')[
            'ingresos_total']
        monthly_memberships = self.monthly_summary.set_index('month')[
            'total_membresías']
        monthly_tickets = self.monthly_summary.set_index('month')[
            'ticket_promedio']
        monthly_customers = self.monthly_summary.set_index('month')[
            'clientes_únicos']

        # Tasas de crecimiento porcentual
        self.stats['growth_rates'] = {
            'ingresos': monthly_revenue.pct_change().fillna(0) * 100,
            'membresias': monthly_memberships.pct_change().fillna(0) * 100,
            'ticket_promedio': monthly_tickets.pct_change().fillna(0) * 100,
            'clientes_unicos': monthly_customers.pct_change().fillna(0) * 100
        }

        # Cambios absolutos
        self.stats['absolute_changes'] = {
            'ingresos': monthly_revenue.diff().fillna(0),
            'membresias': monthly_memberships.diff().fillna(0),
            'ticket_promedio': monthly_tickets.diff().fillna(0),
            'clientes_unicos': monthly_customers.diff().fillna(0)
        }

        # Análisis de crecimiento por planes
        self._calculate_plan_growth()

    def _calculate_plan_growth(self):
        """Calcula el crecimiento por planes"""
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

        self.stats['plan_growth'] = plan_evolution

    def _calculate_trends(self):
        """Calcula tendencias y patrones"""
        monthly_revenue = self.monthly_summary.set_index('month')[
            'ingresos_total']
        monthly_memberships = self.monthly_summary.set_index('month')[
            'total_membresías']

        self.stats['trends'] = {
            'mejor_mes_ingresos': monthly_revenue.idxmax(),
            'peor_mes_ingresos': monthly_revenue.idxmin(),
            'mejor_mes_membresias': monthly_memberships.idxmax(),
            'mayor_crecimiento_ingresos': self.stats['growth_rates']['ingresos'].idxmax(),
            'mayor_caida_ingresos': self.stats['growth_rates']['ingresos'].idxmin(),
            'promedio_crecimiento_ingresos': self.stats['growth_rates']['ingresos'].mean(),
            'promedio_crecimiento_membresias': self.stats['growth_rates']['membresias'].mean()
        }

        # Identificar el mejor plan por crecimiento
        self.stats['trends']['mejor_plan_crecimiento'] = self._get_best_growing_plan()

    def _get_best_growing_plan(self):
        """Identifica el plan con mejor crecimiento promedio"""
        best_growth = -float('inf')
        best_plan = 'N/A'

        for plan, data in self.stats['plan_growth'].items():
            if len(data['revenue_growth']) > 0:
                avg_growth = data['revenue_growth'].mean()
                if avg_growth > best_growth:
                    best_growth = avg_growth
                    best_plan = plan

        return best_plan

    def _calculate_projections(self):
        """Calcula proyecciones para el siguiente mes"""
        monthly_revenue = self.monthly_summary.set_index('month')[
            'ingresos_total']
        monthly_memberships = self.monthly_summary.set_index('month')[
            'total_membresías']

        if len(monthly_revenue) >= 2:
            # Proyección basada en tendencia lineal simple
            revenue_trend = monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2]
            membership_trend = monthly_memberships.iloc[-1] - \
                monthly_memberships.iloc[-2]

            self.stats['projections'] = {
                'agosto_ingresos_estimados': monthly_revenue.iloc[-1] + revenue_trend,
                'agosto_membresias_estimadas': monthly_memberships.iloc[-1] + membership_trend,
                'tendencia_ingresos': 'Creciente' if revenue_trend > 0 else 'Decreciente',
                'tendencia_membresias': 'Creciente' if membership_trend > 0 else 'Decreciente'
            }

            # Proyección más sofisticada usando promedio móvil
            if len(monthly_revenue) >= 3:
                revenue_ma = monthly_revenue.rolling(window=2).mean().iloc[-1]
                membership_ma = monthly_memberships.rolling(
                    window=2).mean().iloc[-1]

                self.stats['projections']['agosto_ingresos_ma'] = revenue_ma
                self.stats['projections']['agosto_membresias_ma'] = membership_ma

    def get_summary_text(self):
        """Genera texto de resumen para el reporte ejecutivo"""
        return f"""
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

    def get_monthly_comparison_data(self):
        """Retorna datos estructurados para comparación mensual"""
        return {
            'months': self.monthly_summary['month'].tolist(),
            'revenue': self.monthly_summary['ingresos_total'].tolist(),
            'memberships': self.monthly_summary['total_membresías'].tolist(),
            'avg_tickets': self.monthly_summary['ticket_promedio'].tolist(),
            'customers': self.monthly_summary['clientes_únicos'].tolist()
        }

    def get_plan_analysis_data(self):
        """Retorna datos estructurados para análisis por planes"""
        return {
            'plan_revenue': self.stats['by_plan']['ingresos'],
            'plan_count': self.stats['by_plan']['cantidad'],
            'plan_tickets': self.stats['by_plan']['ticket_promedio'],
            'plan_distribution': self.combined_df['membership_plan_name'].value_counts()
        }
