#!/usr/bin/env python3
"""
Generador de Reporte PDF - Análisis Total de Pagos (Refactorizado)
Analiza todos los pagos (membresías, productos, reconsumos, upgrades) de mayo, junio y julio 2024

Este es el punto de entrada principal que utiliza los módulos refactorizados
en la carpeta src/total/ para mayor modularidad y mantenibilidad.
"""

from src.total.config import MESSAGES, DEFAULT_OUTPUT_PATH, CATEGORY_NAMES
from src.total import TotalDataLoader, TotalAnalytics, TotalReportGenerator
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


class TotalPaymentsReportRunner:
    """Coordinador principal para ejecutar el análisis completo de pagos totales"""

    def __init__(self, data_path="data/total/", output_file=DEFAULT_OUTPUT_PATH):
        self.data_path = data_path
        self.output_file = output_file
        self.data_loader = None
        self.analytics = None
        self.report_generator = None

    def run_complete_analysis(self):
        """Ejecuta el análisis completo de pagos totales"""
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
        self.data_loader = TotalDataLoader(self.data_path)

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

        # Mostrar reporte de calidad
        quality_report = self.data_loader.get_data_quality_report()
        if quality_report:
            print(
                f"📊 Calidad de datos: {quality_report['total_records']} registros procesados")

    def _perform_analytics(self):
        """Realiza todos los cálculos analíticos"""
        data = self.data_loader.get_data()

        self.analytics = TotalAnalytics(
            data['combined_df'],
            data['monthly_summary'],
            data['monthly_category_summary']
        )

        # Calcular todas las estadísticas
        stats = self.analytics.calculate_all_stats()

        # Detectar anomalías
        anomalies = self.analytics.detect_anomalies()
        if anomalies:
            print("⚠️  Anomalías detectadas:")
            for anomaly in anomalies:
                print(f"   - {anomaly}")

        print(
            f"✅ Estadísticas calculadas: {len(stats)} categorías de análisis")

    def _generate_report(self):
        """Genera el reporte PDF completo"""
        data = self.data_loader.get_data()
        stats = self.analytics.stats

        self.report_generator = TotalReportGenerator(
            data['combined_df'],
            data['monthly_summary'],
            data['monthly_category_summary'],
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

        print("\n📊 RESUMEN DEL ANÁLISIS TOTAL:")
        print("-" * 50)
        print(f"💰 Ingresos Totales: S/ {stats['total_revenue']:,.2f}")
        print(f"📝 Total Transacciones: {stats['total_transactions']}")
        print(f"👥 Clientes Únicos: {stats['unique_customers']}")
        print(f"🎯 Ticket Promedio: S/ {stats['avg_ticket']:,.2f}")
        print(f"📈 Mejor Mes: {stats['trends']['mejor_mes_ingresos']}")
        print(f"🏆 Mejor Categoría: {stats['trends']['mejor_categoria']}")
        print(
            f"🚀 Mayor Crecimiento: {stats['trends']['categoria_mas_crecimiento']}")
        print(
            f"🔮 Proyección Agosto: S/ {stats['projections']['agosto_ingresos_estimados']:,.0f}")
        print(
            f"📊 Diversificación: {stats['diversity']['concentration_level']}")
        print(f"📄 Archivo Generado: {self.output_file}")

        # Mostrar desglose por categorías
        print(f"\n📋 DESGLOSE POR CATEGORÍAS:")
        for category, revenue in stats['by_category']['ingresos'].items():
            participation = stats['category_participation'][category]
            print(f"   • {category}: S/ {revenue:,.0f} ({participation:.1f}%)")

    def generate_excel_export(self, excel_file="datos_totales_detallados.xlsx"):
        """Genera exportación adicional a Excel"""
        if self.report_generator:
            self.report_generator.export_data_to_excel(excel_file)
            return True
        return False

    def get_business_intelligence_summary(self):
        """Retorna resumen de inteligencia de negocios"""
        if self.report_generator:
            return self.report_generator.generate_business_intelligence_summary()
        return None

    def get_dashboard_data(self):
        """Retorna datos estructurados para dashboard"""
        if self.report_generator:
            return self.report_generator.create_dashboard_data()
        return None

    def get_quick_stats(self):
        """Retorna estadísticas rápidas para uso programático"""
        if not self.analytics:
            return None

        return self.analytics.stats


def print_project_info():
    """Muestra información sobre la estructura del proyecto"""
    print("\n" + "="*60)
    print("ANÁLISIS TOTAL DE PAGOS - VERSIÓN REFACTORIZADA")
    print("="*60)
    print("📁 ESTRUCTURA DEL PROYECTO:")
    print("├── total.py                   # 🎯 Script principal (este archivo)")
    print("├── membership.py              # 📊 Script de análisis de membresías")
    print("├── data/total/                # 📂 Datos de pagos totales")
    print("└── src/total/                 # 🔧 Módulos refactorizados:")
    print("    ├── __init__.py           #    📦 Inicialización del paquete")
    print("    ├── config.py             #    ⚙️  Configuraciones")
    print("    ├── data_loader.py        #    📥 Carga de datos")
    print("    ├── analytics.py          #    🧮 Cálculos estadísticos")
    print("    ├── visualizations.py     #    📊 Creación de gráficos")
    print("    └── report_generator.py   #    📄 Generación de PDF")
    print("\n🎯 CATEGORÍAS ANALIZADAS:")
    for key, value in CATEGORY_NAMES.items():
        print(f"   • {value} ({key})")
    print("\n🎯 VENTAJAS DE LA REFACTORIZACIÓN:")
    print("✅ Análisis integral de todo el negocio")
    print("✅ Código modular y mantenible")
    print("✅ Métricas de diversificación")
    print("✅ Detección de anomalías")
    print("✅ Proyecciones avanzadas")
    print("✅ Exportación a múltiples formatos")


def show_analysis_capabilities():
    """Muestra las capacidades de análisis disponibles"""
    print("\n📊 CAPACIDADES DE ANÁLISIS:")
    print("-" * 40)
    print("📈 ANÁLISIS TEMPORAL:")
    print("   • Evolución mensual de ingresos")
    print("   • Tasas de crecimiento por período")
    print("   • Detección de estacionalidad")
    print("   • Proyecciones futuras")

    print("\n🏷️  ANÁLISIS POR CATEGORÍAS:")
    print("   • Rendimiento por tipo de pago")
    print("   • Crecimiento por categoría")
    print("   • Participación en ingresos totales")
    print("   • Mapas de calor categoría-mes")

    print("\n📊 MÉTRICAS DE NEGOCIO:")
    print("   • Diversificación de ingresos")
    print("   • Concentración de categorías")
    print("   • Ticket promedio y mediano")
    print("   • Retención de clientes")

    print("\n🔍 DETECCIÓN DE PATRONES:")
    print("   • Anomalías en transacciones")
    print("   • Caídas significativas")
    print("   • Tendencias de crecimiento")
    print("   • Análisis de volatilidad")


def main():
    """Función principal"""
    print_project_info()
    show_analysis_capabilities()

    # Verificar dependencias
    print("\n🔍 Verificando dependencias...")
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        print("✅ Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"❌ Falta instalar: {e}")
        print("Ejecuta: pip install pandas matplotlib seaborn numpy")
        return 1

    # Verificar estructura de carpetas
    print("🔍 Verificando estructura de carpetas...")
    data_path = Path("data/total/")
    src_path = Path("src/total/")

    if not data_path.exists():
        print(f"❌ No se encuentra la carpeta: {data_path}")
        print("Asegúrate de tener los archivos CSV en data/total/")
        return 1

    if not src_path.exists():
        print(f"❌ No se encuentra la carpeta: {src_path}")
        print("Asegúrate de tener los módulos en src/total/")
        return 1

    print("✅ Estructura de carpetas correcta")

    # Ejecutar análisis
    try:
        runner = TotalPaymentsReportRunner()
        runner.run_complete_analysis()

        # Mostrar inteligencia de negocios
        print("\n🧠 INTELIGENCIA DE NEGOCIOS:")
        bi_summary = runner.get_business_intelligence_summary()
        if bi_summary:
            print(
                f"   📊 Tasa de crecimiento promedio: {bi_summary['kpis']['revenue_growth_rate']:.1f}%")
            print(
                f"   🎯 Categoría líder: {bi_summary['category_performance']['leader']}")
            print(
                f"   🚀 Mayor crecimiento: {bi_summary['category_performance']['fastest_growing']}")
            print(
                f"   ⚖️  Riesgo de concentración: {bi_summary['category_performance']['concentration_risk']}")

        # Opciones adicionales
        print("\n📊 OPCIONES ADICIONALES:")
        print("1. Generar archivo Excel detallado")
        print("2. Mostrar datos para dashboard")
        print("3. Continuar sin opciones adicionales")

        try:
            choice = input("\nSelecciona una opción (1-3): ").strip()

            if choice == "1":
                print("📈 Generando archivo Excel...")
                if runner.generate_excel_export():
                    print("✅ Archivo Excel generado: datos_totales_detallados.xlsx")

            elif choice == "2":
                print("📊 Generando datos para dashboard...")
                dashboard_data = runner.get_dashboard_data()
                if dashboard_data:
                    print("✅ Datos de dashboard disponibles")
                    print("📋 Estructura de datos:")
                    for key in dashboard_data.keys():
                        print(f"   • {key}")

            else:
                print("✅ Continuando sin opciones adicionales")

        except (KeyboardInterrupt, EOFError):
            print("\n✅ Continuando sin opciones adicionales")

        print("\n🎉 ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("\n📋 ARCHIVOS GENERADOS:")
        print(f"   📄 PDF Principal: {DEFAULT_OUTPUT_PATH}")
        if choice == "1":
            print("   📊 Excel Detallado: datos_totales_detallados.xlsx")

        print("\n🎯 INSIGHTS PRINCIPALES:")
        stats = runner.get_quick_stats()
        if stats:
            print(f"   💰 Ingresos: S/ {stats['total_revenue']:,.0f}")
            print(
                f"   📈 Mejor categoría: {stats['trends']['mejor_categoria']}")
            print(
                f"   🚀 Proyección: {stats['projections']['tendencia_ingresos']}")

        return 0

    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        print("Revisa los datos y la configuración")
        return 1


def run_quick_analysis():
    """Ejecuta un análisis rápido sin generar PDF"""
    print("🚀 ANÁLISIS RÁPIDO - SOLO ESTADÍSTICAS")
    print("="*40)

    try:
        runner = TotalPaymentsReportRunner()
        runner._load_and_prepare_data()
        runner._perform_analytics()

        stats = runner.get_quick_stats()
        if stats:
            print("\n📊 ESTADÍSTICAS RÁPIDAS:")
            print(f"💰 Ingresos Totales: S/ {stats['total_revenue']:,.2f}")
            print(f"📝 Transacciones: {stats['total_transactions']}")
            print(f"👥 Clientes: {stats['unique_customers']}")
            print(f"🎯 Ticket Promedio: S/ {stats['avg_ticket']:,.2f}")
            print(f"🏆 Mejor Categoría: {stats['trends']['mejor_categoria']}")

            # Mostrar crecimiento por mes
            growth_rates = stats['growth_rates']['ingresos']
            print(f"\n📈 CRECIMIENTO MENSUAL:")
            for month, rate in growth_rates.items():
                print(f"   • {month}: {rate:+.1f}%")

    except Exception as e:
        print(f"❌ Error en análisis rápido: {e}")
        return 1

    return 0


if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick" or sys.argv[1] == "-q":
            exit_code = run_quick_analysis()
            exit(exit_code)
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Uso:")
            print("  python total.py           # Análisis completo con PDF")
            print("  python total.py --quick   # Análisis rápido solo estadísticas")
            print("  python total.py --help    # Mostrar esta ayuda")
            exit(0)

    exit_code = main()
    exit(exit_code)
