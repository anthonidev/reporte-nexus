"""
Módulo para cargar y preparar datos de membresías
"""

import pandas as pd
from .config import DEFAULT_DATA_PATH, MONTHS, MONTH_NAMES, MESSAGES


class DataLoader:
    """Maneja la carga y preparación de datos de membresías"""

    def __init__(self, data_path=DEFAULT_DATA_PATH):
        self.data_path = data_path
        self.dfs = {}
        self.combined_df = None
        self.monthly_summary = None

    def load_data(self):
        """Carga los datos de los 3 meses"""
        for month in MONTHS:
            file_path = f"{self.data_path}membership-{month}.csv"
            try:
                df = pd.read_csv(file_path)
                df['month'] = MONTH_NAMES[month]
                df['month_order'] = MONTHS.index(month) + 1
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
        self.combined_df['membership_plan_name'] = (
            self.combined_df['membership_plan_name'].str.strip()
        )
        self.combined_df['amount'] = pd.to_numeric(
            self.combined_df['amount'], errors='coerce'
        )

        # Crear resumen por mes
        self._create_monthly_summary()

    def _create_monthly_summary(self):
        """Crea el resumen mensual"""
        self.monthly_summary = self.combined_df.groupby(['month', 'month_order']).agg({
            'amount': ['sum', 'mean', 'count'],
            'email': 'nunique'
        }).round(2)

        self.monthly_summary.columns = [
            'ingresos_total', 'ticket_promedio', 'total_membresías', 'clientes_únicos'
        ]
        self.monthly_summary = (
            self.monthly_summary.reset_index().sort_values('month_order')
        )

    def get_data(self):
        """Retorna los datos procesados"""
        if self.combined_df is None:
            raise ValueError(
                "Los datos no han sido preparados. Ejecuta prepare_data() primero.")

        return {
            'combined_df': self.combined_df,
            'monthly_summary': self.monthly_summary,
            'individual_dfs': self.dfs
        }

    def validate_data(self):
        """Valida que los datos estén correctamente cargados"""
        issues = []

        if self.combined_df is None:
            issues.append("Datos no preparados")
            return issues

        # Verificar columnas requeridas
        required_columns = ['amount', 'membership_plan_name', 'email', 'month']
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

        return issues
