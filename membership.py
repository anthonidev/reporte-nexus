#!/usr/bin/env python3


from src.membership.config import MESSAGES, DEFAULT_OUTPUT_PATH
from src.membership import DataLoader, MembershipAnalytics, ReportGenerator
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


class MembershipReportRunner:
    """Coordinador principal para ejecutar el análisis completo de membresías"""

    def __init__(self, data_path="data/membership/", output_file=DEFAULT_OUTPUT_PATH):
        self.data_path = data_path
        self.output_file = output_file
        self.data_loader = None
        self.analytics = None
        self.report_generator = None

    def run_complete_analysis(self):
        """Ejecuta el análisis completo de membresías"""
        try:
            print(MESSAGES['analysis_start'])
            print("="*60)

            # Paso 1: Cargar y preparar datos
            print("📊 Paso 1: Cargando datos...")
            self._load_and_prepare_data()

            # Paso 2: Realizar análisis estadísticos
            print("📈 Paso 2: Calculando estadísticas...")
            self._perform_analytics()

            # Paso 3: Generar reporte PDF
            print("📄 Paso 3: Generando reporte PDF...")
            self._generate_report()

            # Paso 4: Mostrar resumen
            print("📋 Paso 4: Mostrando resumen...")
            self._show_summary()

            print("="*60)
            print("✅ " + MESSAGES['analysis_complete'])

        except Exception as e:
            print(f"❌ Error durante el análisis: {e}")
            raise

    def _load_and_prepare_data(self):
        """Carga y prepara los datos"""
        self.data_loader = DataLoader(self.data_path)

        # Cargar datos de archivos CSV
        self.data_loader.load_data()

        # Preparar y combinar datos
        self.data_loader.prepare_data()

        # Validar datos cargados
        issues = self.data_loader.validate_data()
        if issues:
            print("⚠️  Problemas encontrados en los datos:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Datos cargados y validados correctamente")

    def _perform_analytics(self):
        """Realiza todos los cálculos analíticos"""
        data = self.data_loader.get_data()

        self.analytics = MembershipAnalytics(
            data['combined_df'],
            data['monthly_summary']
        )

        # Calcular todas las estadísticas
        stats = self.analytics.calculate_all_stats()

        print(f"✅ Estadísticas calculadas: {len(stats)} categorías")

    def _generate_report(self):
        """Genera el reporte PDF completo"""
        data = self.data_loader.get_data()
        stats = self.analytics.stats

        self.report_generator = ReportGenerator(
            data['combined_df'],
            data['monthly_summary'],
            stats
        )

        # Validar antes de generar
        issues = self.report_generator.validate_report_generation()
        if issues:
            print("⚠️  Problemas encontrados para generar el reporte:")
            for issue in issues:
                print(f"   - {issue}")
            return

        # Generar PDF
        self.report_generator.generate_pdf_report(self.output_file)

        print("✅ Reporte PDF generado exitosamente")

    def _show_summary(self):
        """Muestra un resumen del análisis"""
        if not self.analytics:
            return

        stats = self.analytics.stats

        print("\n📊 RESUMEN DEL ANÁLISIS:")
        print("-" * 40)
        print(f"💰 Ingresos Totales: S/ {stats['total_revenue']:,.2f}")
        print(f"📝 Total Membresías: {stats['total_memberships']}")
        print(f"👥 Clientes Únicos: {stats['unique_customers']}")
        print(f"🎯 Ticket Promedio: S/ {stats['avg_ticket']:,.2f}")
        print(f"📈 Mejor Mes: {stats['trends']['mejor_mes_ingresos']}")
        print(f"🏆 Mejor Plan: {stats['by_plan'].index[0]}")
        print(
            f"🔮 Proyección Agosto: S/ {stats['projections']['agosto_ingresos_estimados']:,.0f}")
        print(f"📄 Archivo Generado: {self.output_file}")

    def generate_excel_export(self, excel_file="datos_membresias_detallados.xlsx"):
        """Genera exportación adicional a Excel"""
        if self.report_generator:
            self.report_generator.export_data_to_excel(excel_file)
            return True
        return False

    def get_quick_stats(self):
        """Retorna estadísticas rápidas para uso programático"""
        if not self.analytics:
            return None

        return self.analytics.stats


def print_project_info():
    """Muestra información sobre la estructura del proyecto"""
    print("\n" + "="*60)
    print("ANÁLISIS DE MEMBRESÍAS - VERSIÓN REFACTORIZADA")
    print("="*60)
    print("📁 ESTRUCTURA DEL PROYECTO:")
    print("├── membership.py              # 🎯 Script principal (este archivo)")
    print("├── total.py                   # 📊 Script de análisis total")
    print("├── data/membership/           # 📂 Datos de membresías")
    print("└── src/membership/            # 🔧 Módulos refactorizados:")
    print("    ├── __init__.py           #    📦 Inicialización del paquete")
    print("    ├── config.py             #    ⚙️  Configuraciones")
    print("    ├── data_loader.py        #    📥 Carga de datos")
    print("    ├── analytics.py          #    🧮 Cálculos estadísticos")
    print("    ├── visualizations.py     #    📊 Creación de gráficos")
    print("    └── report_generator.py   #    📄 Generación de PDF")
    print("\n🎯 VENTAJAS DE LA REFACTORIZACIÓN:")
    print("✅ Código más limpio y mantenible")
    print("✅ Responsabilidades separadas")
    print("✅ Fácil testing de componentes")
    print("✅ Extensibilidad mejorada")
    print("✅ Reutilización de código")


def main():
    """Función principal"""
    print_project_info()

    # Verificar dependencias
    print("\n🔍 Verificando dependencias...")
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✅ Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"❌ Falta instalar: {e}")
        print("Ejecuta: pip install pandas matplotlib seaborn")
        return 1

    # Verificar estructura de carpetas
    print("🔍 Verificando estructura de carpetas...")
    data_path = Path("data/membership/")
    src_path = Path("src/membership/")

    if not data_path.exists():
        print(f"❌ No se encuentra la carpeta: {data_path}")
        print("Asegúrate de tener los archivos CSV en data/membership/")
        return 1

    if not src_path.exists():
        print(f"❌ No se encuentra la carpeta: {src_path}")
        print("Asegúrate de tener los módulos en src/membership/")
        return 1

    print("✅ Estructura de carpetas correcta")

    # Ejecutar análisis
    try:
        runner = MembershipReportRunner()
        runner.run_complete_analysis()

        # Opción adicional: generar Excel
        print("\n📊 ¿Deseas generar también un archivo Excel con los datos? (y/n): ", end="")
        response = input().lower().strip()

        if response in ['y', 'yes', 'sí', 's']:
            print("📈 Generando archivo Excel...")
            if runner.generate_excel_export():
                print("✅ Archivo Excel generado: datos_membresias_detallados.xlsx")

        print("\n🎉 ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("\n📋 ARCHIVOS GENERADOS:")
        print(f"   📄 PDF: {DEFAULT_OUTPUT_PATH}")
        if response in ['y', 'yes', 'sí', 's']:
            print("   📊 Excel: datos_membresias_detallados.xlsx")

        return 0

    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        print("Revisa los datos y la configuración")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
