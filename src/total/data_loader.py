"""
Módulo para cargar y preparar datos de pagos totales
"""

import pandas as pd
from .config import DEFAULT_DATA_PATH, MONTHS, MONTH_NAMES, CATEGORY_NAMES, MESSAGES


class TotalDataLoader:
    """Maneja la carga y preparación de datos de todos los tipos de pagos"""

    def __init__(self, data_path=DEFAULT_DATA_PATH):
        self.data_path = data_path
        self.dfs = {}
        self.combined_df = None
        self.monthly_summary = None
        self.monthly_category_summary = None

    def load_data(self):
        """Carga los datos de los 3 meses"""
        for month in MONTHS:
            file_path = f"{self.data_path}total-{month}.csv"
            try:
                df = pd.read_csv(file_path)
                df['month'] = MONTH_NAMES[month]
                df['month_order'] = MONTHS.index(month) + 1
                # Limpiar categorías
                df['category_clean'] = df['relatedEntityType'].map(
                    CATEGORY_NAMES).fillna(df['relatedEntityType'])
                self.dfs[month] = df
                print(MESSAGES['loading_success'].format(
                    file_path=file_path, records=len(df)
                ))
            except FileNotFoundError:
                print(MESSAGES['loading_error'].format(file_path=file_path))

    def prepare_data(self):
        """Prepara y combina los datos"""
        if not self.dfs:
            raise ValueError(
                "No se cargaron datos. Ejecuta load_data() primero.")

        # Combinar todos los dataframes
        self.combined_df = pd.concat(self.dfs.values(), ignore_index=True)

        # Limpiar y estandarizar datos
        self.combined_df['amount'] = pd.to_numeric(
            self.combined_df['amount'], errors='coerce'
        )
        self.combined_df = self.combined_df.dropna(subset=['amount'])

        # Crear resúmenes
        self._create_monthly_summary()
        self._create_monthly_category_summary()

    def _create_monthly_summary(self):
        """Crea el resumen mensual total"""
        self.monthly_summary = self.combined_df.groupby(['month', 'month_order']).agg({
            'amount': ['sum', 'mean', 'count'],
            'email': 'nunique'
        }).round(2)

        self.monthly_summary.columns = [
            'ingresos_total', 'ticket_promedio', 'total_transacciones', 'clientes_únicos'
        ]
        self.monthly_summary = (
            self.monthly_summary.reset_index().sort_values('month_order')
        )

    def _create_monthly_category_summary(self):
        """Crea el resumen mensual por categoría"""
        self.monthly_category_summary = self.combined_df.groupby([
            'month', 'month_order', 'category_clean'
        ]).agg({
            'amount': ['sum', 'mean', 'count'],
            'email': 'nunique'
        }).round(2)

        self.monthly_category_summary.columns = [
            'ingresos_total', 'ticket_promedio', 'total_transacciones', 'clientes_únicos'
        ]
        self.monthly_category_summary = (
            self.monthly_category_summary.reset_index()
        )

    def get_data(self):
        """Retorna los datos procesados"""
        if self.combined_df is None:
            raise ValueError(
                "Los datos no han sido preparados. Ejecuta prepare_data() primero.")

        return {
            'combined_df': self.combined_df,
            'monthly_summary': self.monthly_summary,
            'monthly_category_summary': self.monthly_category_summary,
            'individual_dfs': self.dfs
        }

    def validate_data(self):
        """Valida que los datos estén correctamente cargados"""
        issues = []

        if self.combined_df is None:
            issues.append("Datos no preparados")
            return issues

        # Verificar columnas requeridas
        required_columns = ['amount', 'relatedEntityType',
                            'email', 'month', 'category_clean']
        missing_columns = [col for col in required_columns
                           if col not in self.combined_df.columns]
        if missing_columns:
            issues.append(f"Columnas faltantes: {missing_columns}")

        # Verificar datos nulos en amount
        null_amounts = self.combined_df['amount'].isnull().sum()
        if null_amounts > 0:
            issues.append(f"{null_amounts} valores nulos en 'amount'")

        # Verificar que hay datos para los 3 meses
        unique_months = self.combined_df['month'].nunique()
        if unique_months != 3:
            issues.append(f"Solo hay datos para {unique_months} meses")

        # Verificar categorías conocidas
        unknown_categories = set(
            self.combined_df['relatedEntityType']) - set(CATEGORY_NAMES.keys())
        if unknown_categories:
            issues.append(f"Categorías desconocidas: {unknown_categories}")

        return issues

    def get_category_summary(self):
        """Retorna resumen por categorías"""
        if self.combined_df is None:
            return None

        return self.combined_df.groupby('category_clean').agg({
            'amount': ['sum', 'count', 'mean'],
            'email': 'nunique'
        }).round(2)

    def get_monthly_evolution_by_category(self):
        """Retorna evolución mensual por categoría"""
        if self.combined_df is None:
            return None

        return self.combined_df.groupby(['month', 'category_clean'])['amount'].sum().unstack(fill_value=0)

    def get_data_quality_report(self):
        """Genera un reporte de calidad de datos"""
        if self.combined_df is None:
            return None

        report = {
            'total_records': len(self.combined_df),
            'unique_customers': self.combined_df['email'].nunique(),
            'date_range': f"{self.combined_df['month'].min()} - {self.combined_df['month'].max()}",
            'categories': self.combined_df['category_clean'].value_counts().to_dict(),
            'null_values': self.combined_df.isnull().sum().to_dict(),
            'duplicates': self.combined_df.duplicated().sum(),
            'amount_stats': {
                'min': self.combined_df['amount'].min(),
                'max': self.combined_df['amount'].max(),
                'mean': self.combined_df['amount'].mean(),
                'median': self.combined_df['amount'].median()
            }
        }

        return report
