#!/usr/bin/env python3
"""
Dashboard QA Completo - Extrae TODAS las estadísticas solicitadas
Con vistas semanales e históricas
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import webbrowser

class ComprehensiveQADashboard:
    def __init__(self, excel_path='reporte_tarjetas.xlsx'):
        self.excel_path = excel_path
        self.all_data = pd.DataFrame()
        self.weeks_list = []
        self.load_all_sheets()

    def load_all_sheets(self):
        """Carga todas las hojas del Excel y las combina"""
        try:
            xl_file = pd.ExcelFile(self.excel_path)

            all_sheets = []
            for sheet_name in xl_file.sheet_names:
                if 'tarjetas semana' in sheet_name.lower():
                    print(f"Cargando: {sheet_name}")
                    df = pd.read_excel(xl_file, sheet_name)
                    df['Semana'] = sheet_name
                    all_sheets.append(df)
                    self.weeks_list.append(sheet_name)

            self.all_data = pd.concat(all_sheets, ignore_index=True)
            self.clean_data()
            print(f"Total de registros cargados: {len(self.all_data)}")
            print(f"Semanas cargadas: {len(self.weeks_list)}")
            print("Columnas del DataFrame después de la carga y limpieza:", self.all_data.columns.tolist()) # Added for debugging

        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            raise

    def clean_data(self):
        """
        Limpia y prepara los datos, estandarizando nombres de columnas
        y manejando valores nulos.
        """
        # Convertir fechas
        date_columns = ['Fecha tentativa  de validación por parte de QA', 'Fecha de Aprobación o Rechazo']
        for col in date_columns:
            if col in self.all_data.columns:
                self.all_data[col] = pd.to_datetime(self.all_data[col], errors='coerce')

        # Clean 'Número de rechazos'
        if 'Número de rechazos' in self.all_data.columns:
            self.all_data['Número de rechazos'] = pd.to_numeric(self.all_data['Número de rechazos'], errors='coerce').fillna(0)
        else:
            print("Warning: 'Número de rechazos' column not found. Setting to 0.")
            self.all_data['Número de rechazos'] = 0

        # Clean 'Aceptado/Rechazado'
        if 'Aceptado/Rechazado' in self.all_data.columns:
            self.all_data['Aceptado/Rechazado'] = self.all_data['Aceptado/Rechazado'].fillna('PENDIENTE')
        else:
            print("Warning: 'Aceptado/Rechazado' column not found. Setting to 'PENDIENTE'.")
            self.all_data['Aceptado/Rechazado'] = 'PENDIENTE'

        # --- Handle 'Desarrollador' column specifically ---
        # Find all columns that might contain developer names (case-insensitive)
        dev_cols = [col for col in self.all_data.columns if 'desarrollador' in col.lower() or 'developer' in col.lower()]

        if 'Desarrollador' not in self.all_data.columns and dev_cols:
            # If 'Desarrollador' doesn't exist but other dev columns do,
            # try to coalesce them into a single 'Desarrollador' column.
            # This assumes that if multiple dev columns exist, only one should have a value per row.
            # bfill(axis=1) fills NaNs backwards along rows, then iloc[:, 0] takes the first non-null.
            self.all_data['Desarrollador'] = self.all_data[dev_cols].bfill(axis=1).iloc[:, 0]
            print(f"Coalesced columns {dev_cols} into 'Desarrollador'.")
            # Drop the original developer columns after coalescing
            self.all_data.drop(columns=dev_cols, inplace=True, errors='ignore')
        elif 'Desarrollador' not in self.all_data.columns and not dev_cols:
            print("Warning: 'Desarrollador' column or its variations not found. Creating an empty 'Desarrollador' column.")
            self.all_data['Desarrollador'] = np.nan

        # Fill any remaining NaNs in 'Desarrollador' with a placeholder
        if 'Desarrollador' in self.all_data.columns:
            self.all_data['Desarrollador'] = self.all_data['Desarrollador'].fillna('Desarrollador Desconocido')

        # --- Standardize other key columns ---
        # This dictionary maps the desired column name to a list of its possible variations (lowercase)
        expected_cols_mapping = {
            'PM': ['pm', 'qa'],
            'Web/App': ['web/app', 'web o app'],
            'Sitio': ['sitio'],
            'Plataforma': ['plataforma'],
            'Prioridad en la Tarjeta': ['prioridad en la tarjeta', 'prioridad']
        }

        for expected_col, variations in expected_cols_mapping.items():
            if expected_col not in self.all_data.columns: # If the desired column name is not present
                found_variation = False
                for col_name in self.all_data.columns:
                    # Check if the current column name (lowercase) is in the variations list
                    if col_name.lower() in variations:
                        self.all_data.rename(columns={col_name: expected_col}, inplace=True)
                        print(f"Renamed column '{col_name}' to '{expected_col}'")
                        found_variation = True
                        break
                if not found_variation:
                    print(f"Warning: Column '{expected_col}' or its variations not found. Creating an empty column.")
                    self.all_data[expected_col] = np.nan


    def get_qa_statistics_complete(self):
        """Estadísticas COMPLETAS de QA - Por semana y totales"""
        qa_stats = {
            'weekly': {},
            'historical': {
                'por_qa': {},
                'total_rechazadas': 0,
                'total_revisadas': 0
            }
        }

        # Por cada semana
        for semana in self.weeks_list:
            week_data = self.all_data[self.all_data['Semana'] == semana]

            # Tarjetas por QA esta semana
            qa_counts = {}
            qa_rechazadas = {}

            for qa in week_data['PM'].dropna().unique():
                qa_data = week_data[week_data['PM'] == qa]
                qa_counts[qa] = len(qa_data)
                qa_rechazadas[qa] = len(qa_data[qa_data['Aceptado/Rechazado'] == 'RECHAZADO'])

            qa_stats['weekly'][semana] = {
                'tarjetas_por_qa': qa_counts,
                'rechazadas_por_qa': qa_rechazadas,
                'total_semana': len(week_data),
                'total_rechazadas_semana': len(week_data[week_data['Aceptado/Rechazado'] == 'RECHAZADO'])
            }

        # Totales históricos
        for qa in self.all_data['PM'].dropna().unique():
            qa_data = self.all_data[self.all_data['PM'] == qa]
            qa_stats['historical']['por_qa'][qa] = {
                'total_revisadas': len(qa_data),
                'total_rechazadas': len(qa_data[qa_data['Aceptado/Rechazado'] == 'RECHAZADO']),
                'promedio_semanal': len(qa_data) / len(self.weeks_list) if len(self.weeks_list) > 0 else 0
            }

        qa_stats['historical']['total_rechazadas'] = len(self.all_data[self.all_data['Aceptado/Rechazado'] == 'RECHAZADO'])
        qa_stats['historical']['total_revisadas'] = len(self.all_data)

        return qa_stats

    def get_web_statistics_complete(self):
        """Estadísticas COMPLETAS Web - Por semana y totales"""
        web_stats = {
            'weekly': {},
            'historical': {
                'total_revisadas': 0,
                'total_rechazadas': 0,
                'total_aceptadas': 0,
                'porcentaje_rechazo': 0
            }
        }

        # Por cada semana
        for semana in self.weeks_list:
            week_data = self.all_data[self.all_data['Semana'] == semana]
            web_data = week_data[week_data['Web/App'] == 'Web']

            total = len(web_data)
            rechazadas = len(web_data[web_data['Aceptado/Rechazado'] == 'RECHAZADO'])
            aceptadas = len(web_data[web_data['Aceptado/Rechazado'] == 'APROBADO'])

            web_stats['weekly'][semana] = {
                'revisadas': total,
                'rechazadas': rechazadas,
                'aceptadas': aceptadas,
                'porcentaje_rechazo': round((rechazadas / total * 100) if total > 0 else 0, 2)
            }

        # Totales históricos
        web_data_total = self.all_data[self.all_data['Web/App'] == 'Web']
        total = len(web_data_total)
        rechazadas = len(web_data_total[web_data_total['Aceptado/Rechazado'] == 'RECHAZADO'])
        aceptadas = len(web_data_total[web_data_total['Aceptado/Rechazado'] == 'APROBADO'])

        web_stats['historical'] = {
            'total_revisadas': total,
            'total_rechazadas': rechazadas,
            'total_aceptadas': aceptadas,
            'porcentaje_rechazo': round((rechazadas / total * 100) if total > 0 else 0, 2)
        }

        return web_stats

    def get_app_statistics_complete(self):
        """Estadísticas COMPLETAS App - Por semana y totales"""
        app_stats = {
            'weekly': {},
            'historical': {
                'total_revisadas': 0,
                'total_rechazadas': 0,
                'total_aceptadas': 0,
                'porcentaje_rechazo': 0
            }
        }

        # Por cada semana
        for semana in self.weeks_list:
            week_data = self.all_data[self.all_data['Semana'] == semana]
            app_data = week_data[week_data['Web/App'] == 'App']

            total = len(app_data)
            rechazadas = len(app_data[app_data['Aceptado/Rechazado'] == 'RECHAZADO'])
            aceptadas = len(app_data[app_data['Aceptado/Rechazado'] == 'APROBADO'])

            app_stats['weekly'][semana] = {
                'revisadas': total,
                'rechazadas': rechazadas,
                'aceptadas': aceptadas,
                'porcentaje_rechazo': round((rechazadas / total * 100) if total > 0 else 0, 2)
            }

        # Totales históricos
        app_data_total = self.all_data[self.all_data['Web/App'] == 'App']
        total = len(app_data_total)
        rechazadas = len(app_data_total[app_data_total['Aceptado/Rechazado'] == 'RECHAZADO'])
        aceptadas = len(app_data_total[app_data_total['Aceptado/Rechazado'] == 'APROBADO'])

        app_stats['historical'] = {
            'total_revisadas': total,
            'total_rechazadas': rechazadas,
            'total_aceptadas': aceptadas,
            'porcentaje_rechazo': round((rechazadas / total * 100) if total > 0 else 0, 2)
        }

        return app_stats

    def get_dev_statistics(self, dev_type):
        """
        Estadísticas COMPLETAS de desarrolladores (Web o App)
        Retorna estadísticas históricas y un desglose semanal detallado por desarrollador.
        """
        filtered_data = self.all_data[self.all_data['Web/App'] == dev_type.capitalize()]
        dev_stats = {}
        dev_weekly_details = {} # To store weekly breakdowns for each dev

        for dev in filtered_data['Desarrollador'].dropna().unique():
            dev_data = filtered_data[filtered_data['Desarrollador'] == dev]

            # Calculate statistics per week for the specific developer
            weekly_summary = {}
            for semana in self.weeks_list:
                week_dev_data = dev_data[dev_data['Semana'] == semana]
                total_week = len(week_dev_data)
                rechazadas_week = len(week_dev_data[week_dev_data['Aceptado/Rechazado'] == 'RECHAZADO'])
                aceptadas_week = len(week_dev_data[week_dev_data['Aceptado/Rechazado'] == 'APROBADO'])
                porcentaje_rechazo_week = round((rechazadas_week / total_week * 100) if total_week > 0 else 0, 2)

                if total_week > 0: # Only include weeks where the developer was active
                    weekly_summary[semana] = {
                        'total_tarjetas': total_week,
                        'rechazadas': rechazadas_week,
                        'aceptadas': aceptadas_week,
                        'porcentaje_rechazo': porcentaje_rechazo_week
                    }
            dev_weekly_details[dev] = weekly_summary


            # Overall historical stats for developer
            total = len(dev_data)
            rechazadas = len(dev_data[dev_data['Aceptado/Rechazado'] == 'RECHAZADO'])
            aceptadas = len(dev_data[dev_data['Aceptado/Rechazado'] == 'APROBADO'])
            promedio_semanal = total / len(self.weeks_list) if len(self.weeks_list) > 0 else 0
            porcentaje_rechazo = round((rechazadas / total * 100) if total > 0 else 0, 2)
            semanas_activo = len(dev_data['Semana'].unique())


            dev_stats[dev] = {
                'total_tarjetas': total,
                'rechazadas': rechazadas,
                'aceptadas': aceptadas,
                'promedio_semanal_historico': round(promedio_semanal, 2),
                'porcentaje_rechazo': porcentaje_rechazo,
                'semanas_activo': semanas_activo
            }

        # Order by total cards
        dev_stats = dict(sorted(dev_stats.items(), key=lambda x: x[1]['total_tarjetas'], reverse=True))

        return dev_stats, dev_weekly_details

    def get_pm_statistics_complete(self):
        """Estadísticas COMPLETAS de PM"""
        pm_stats = {
            'prioridades': {
                'alta': {
                    'total': len(self.all_data[self.all_data['Prioridad en la Tarjeta'] == 'Alta']),
                    'promedio_semanal': 0
                },
                'media': {
                    'total': len(self.all_data[self.all_data['Prioridad en la Tarjeta'] == 'Media']),
                    'promedio_semanal': 0
                },
                'baja': {
                    'total': len(self.all_data[self.all_data['Prioridad en la Tarjeta'] == 'Baja']),
                    'promedio_semanal': 0
                }
            },
            'promedio_semanal': {
                'web': 0,
                'app': 0,
                'total': 0
            },
            'por_semana': {}
        }

        # Calcular promedios
        num_semanas = len(self.weeks_list)
        if num_semanas > 0:
            pm_stats['prioridades']['alta']['promedio_semanal'] = round(pm_stats['prioridades']['alta']['total'] / num_semanas, 2)
            pm_stats['prioridades']['media']['promedio_semanal'] = round(pm_stats['prioridades']['media']['total'] / num_semanas, 2)
            pm_stats['prioridades']['baja']['promedio_semanal'] = round(pm_stats['prioridades']['baja']['total'] / num_semanas, 2)

            # Promedios por tipo
            web_por_semana = self.all_data[self.all_data['Web/App'] == 'Web'].groupby('Semana').size()
            app_por_semana = self.all_data[self.all_data['Web/App'] == 'App'].groupby('Semana').size()

            pm_stats['promedio_semanal']['web'] = round(web_por_semana.mean(), 2) if not web_por_semana.empty else 0
            pm_stats['promedio_semanal']['app'] = round(app_por_semana.mean(), 2) if not app_por_semana.empty else 0
            pm_stats['promedio_semanal']['total'] = round((pm_stats['promedio_semanal']['web'] + pm_stats['promedio_semanal']['app']), 2)


        # Desglose por semana
        for semana in self.weeks_list:
            week_data = self.all_data[self.all_data['Semana'] == semana]
            pm_stats['por_semana'][semana] = {
                'alta': len(week_data[week_data['Prioridad en la Tarjeta'] == 'Alta']),
                'media': len(week_data[week_data['Prioridad en la Tarjeta'] == 'Media']),
                'baja': len(week_data[week_data['Prioridad en la Tarjeta'] == 'Baja']),
                'web': len(week_data[week_data['Web/App'] == 'Web']),
                'app': len(week_data[week_data['Web/App'] == 'App'])
            }

        return pm_stats

    def get_site_statistics_complete(self):
        """Estadísticas COMPLETAS por sitio"""
        site_stats = {}

        for sitio in self.all_data['Sitio'].dropna().unique():
            site_data = self.all_data[self.all_data['Sitio'] == sitio]

            # Totales
            total = len(site_data)
            web = len(site_data[site_data['Web/App'] == 'Web'])
            app = len(site_data[site_data['Web/App'] == 'App'])
            rechazadas = len(site_data[site_data['Aceptado/Rechazado'] == 'RECHAZADO'])
            aceptadas = len(site_data[site_data['Aceptado/Rechazado'] == 'APROBADO'])

            # Promedios
            num_semanas = site_data['Semana'].nunique()
            promedio_total = total / num_semanas if num_semanas > 0 else 0
            promedio_rechazadas = rechazadas / num_semanas if num_semanas > 0 else 0
            promedio_aceptadas = aceptadas / num_semanas if num_semanas > 0 else 0

            # Plataformas
            plataformas = site_data['Plataforma'].value_counts().to_dict()

            site_stats[sitio] = {
                'total': total,
                'web': web,
                'app': app,
                'rechazadas': rechazadas,
                'aceptadas': aceptadas,
                'promedio_por_semana': round(promedio_total, 2),
                'promedio_rechazadas_semana': round(promedio_rechazadas, 2),
                'promedio_aceptadas_semana': round(promedio_aceptadas, 2),
                'plataformas': plataformas,
                'semanas_activo': num_semanas
            }

        # Ordenar por total
        site_stats = dict(sorted(site_stats.items(), key=lambda x: x[1]['total'], reverse=True))

        return site_stats

    def get_platform_report(self):
        """Reporte de número de tarjetas por plataforma"""
        platform_counts = self.all_data['Plataforma'].value_counts().to_dict()

        # Limpiar valores nulos
        cleaned_counts = {}
        for k, v in platform_counts.items():
            if pd.isna(k):
                cleaned_counts['Sin especificar'] = v
            else:
                cleaned_counts[k] = v

        return cleaned_counts

    def generate_all_statistics(self):
        """Genera TODAS las estadísticas solicitadas"""
        print("Generando estadísticas completas...")

        dev_web_stats, dev_web_weekly = self.get_dev_statistics('web')
        dev_app_stats, dev_app_weekly = self.get_dev_statistics('app')

        stats = {
            'qa': self.get_qa_statistics_complete(),
            'web': self.get_web_statistics_complete(),
            'app': self.get_app_statistics_complete(),
            'dev_web': dev_web_stats,
            'dev_app': dev_app_stats,
            'dev_web_weekly_details': dev_web_weekly, # New: detailed weekly stats for web devs
            'dev_app_weekly_details': dev_app_weekly, # New: detailed weekly stats for app devs
            'pm': self.get_pm_statistics_complete(),
            'sites': self.get_site_statistics_complete(),
            'platforms': self.get_platform_report(),
            'weeks_list': self.weeks_list,
            'total_weeks': len(self.weeks_list)
        }

        return stats

    def generate_html_dashboard(self, stats):
        """Genera el dashboard HTML con TODAS las métricas"""
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard QA - Métricas</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {
            --primary-color: #4A00E0;
            --secondary-color: #8E2DE2;
            --accent-color: #00C9FF;
            --background-light: #F0F2F5;
            --card-background: #FFFFFF;
            --text-dark: #1C1E21;
            --text-medium: #65676B;
            --text-light: #A0A3A7;
            --border-light: #E0E0E0;
            --success-color: #27AE60;
            --warning-color: #F39C12;
            --danger-color: #E74C3C;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--background-light);
            color: var(--text-dark);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            text-align: center;
        }

        h1 {
            font-size: 2.8em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .timestamp {
            opacity: 0.9;
            font-size: 0.9em;
            font-weight: 300;
        }

        .nav-tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .tab-button {
            padding: 14px 28px;
            background: var(--card-background);
            border: none; /* Removed border */
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            font-size: 1.05em;
            color: var(--text-medium);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05); /* Subtle shadow */
        }

        .tab-button:hover {
            background: var(--background-light);
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .tab-button.active {
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transform: translateY(-1px);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--card-background);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .stat-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 25px rgba(0,0,0,0.15);
        }

        .stat-value {
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 10px 0;
            line-height: 1;
        }

        .stat-label {
            color: var(--text-medium);
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .section-title {
            font-size: 2.2em;
            color: var(--text-dark);
            margin: 40px 0 25px 0;
            padding-bottom: 12px;
            border-bottom: 4px solid var(--primary-color);
            font-weight: 700;
        }

        table {
            width: 100%;
            background: var(--card-background);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            border-collapse: separate; /* For rounded corners */
            border-spacing: 0; /* For rounded corners */
        }

        th {
            background: var(--primary-color);
            color: white;
            padding: 18px 20px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        
        th:first-child { border-top-left-radius: 15px; }
        th:last-child { border-top-right-radius: 15px; }

        td {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-dark);
        }

        tr:nth-child(even) {
            background-color: #F8F9FA; /* Light stripe */
        }

        tr:hover {
            background-color: #EBF2FF; /* Lighter blue on hover */
        }

        tr:last-child td {
            border-bottom: none;
        }
        
        tr:last-child td:first-child { border-bottom-left-radius: 15px; }
        tr:last-child td:last-child { border-bottom-right-radius: 15px; }


        .percentage {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 0.88em;
            transition: all 0.2s ease;
        }

        .percentage.high {
            background-color: #FEECEB;
            color: var(--danger-color);
        }

        .percentage.medium {
            background-color: #FFF8D4;
            color: var(--warning-color);
        }

        .percentage.low {
            background-color: #D4EDDA;
            color: var(--success-color);
        }

        .chart-container {
            background: var(--card-background);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }

        .info-box {
            background: #F8F9FA;
            border-left: 5px solid var(--primary-color);
            padding: 25px;
            margin: 25px 0;
            border-radius: 10px;
            color: var(--text-dark);
            font-size: 1.05em;
        }

        .info-box h3 {
            color: var(--primary-color);
            margin-bottom: 15px;
            font-size: 1.6em;
            font-weight: 600;
        }
        .info-box p {
            margin-bottom: 8px;
        }
        .info-box strong {
            color: var(--text-dark);
        }

        .metric-group {
            background: #F8F9FA;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid var(--border-light);
        }

        .metric-group h4 {
            color: var(--primary-color);
            margin-bottom: 10px;
            font-size: 1.3em;
            font-weight: 600;
        }

        .week-selector {
            margin: 25px 0;
            padding: 20px;
            background: var(--card-background);
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .week-selector label {
            font-size: 1.1em;
            font-weight: 500;
            color: var(--text-dark);
        }

        .week-selector select {
            padding: 10px 18px;
            font-size: 1em;
            border: 2px solid var(--border-light);
            border-radius: 8px;
            background: white;
            cursor: pointer;
            appearance: none; /* Remove default arrow */
            background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23666%22%20d%3D%22M287%2C114.7L154.7%2C247c-2.3%2C2.3-5.3%2C3.5-8.3%2C3.5s-6.1-1.2-8.3-3.5L5.4%2C114.7c-4.5-4.5-4.5-11.7%2C0-16.2l16.2-16.2c4.5-4.5%2C11.7-4.5%2C16.2%2C0L146%2C178.4l108.2-108.2c4.5-4.5%2C11.7-4.5%2C16.2%2C0l16.2%2C16.2C291.5%2C103%2C291.5%2C110.2%2C287%2C114.7z%22%2F%3E%3C%2Fsvg%3E');
            background-repeat: no-repeat;
            background-position: right 15px top 50%;
            background-size: 0.65em auto;
            min-width: 200px;
        }

        .highlight {
            background: #FFF3CD;
            padding: 3px 8px;
            border-radius: 5px;
            font-weight: 600;
            color: var(--warning-color);
        }

        .small-text {
            font-size: 0.88em;
            color: var(--text-medium);
        }

        .developer-table-row {
            cursor: pointer;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .header {
                padding: 30px 20px;
            }
            h1 {
                font-size: 2em;
            }
            .nav-tabs {
                flex-direction: column;
                align-items: stretch;
            }
            .tab-button {
                width: 100%;
                text-align: center;
            }
            .stats-grid {
                grid-template-columns: 1fr;
            }
            .stat-card {
                padding: 25px;
            }
            .stat-value {
                font-size: 2.5em;
            }
            .section-title {
                font-size: 1.8em;
            }
            table {
                display: block;
                overflow-x: auto;
                white-space: nowrap;
                -webkit-overflow-scrolling: touch; /* for smooth scrolling on iOS */
            }
            table thead, table tbody, table th, table td, table tr {
                display: block;
            }
            table tr {
                margin-bottom: 15px;
                border: 1px solid var(--border-light);
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            table td {
                border-bottom: 1px solid var(--border-light);
                text-align: right;
                padding-left: 50%;
                position: relative;
            }
            table td::before {
                content: attr(data-label);
                position: absolute;
                left: 10px;
                width: calc(50% - 20px);
                padding-right: 10px;
                white-space: nowrap;
                text-align: left;
                font-weight: 600;
                color: var(--text-dark);
            }
            table th {
                display: none; /* Hide original headers */
            }
            .week-selector {
                flex-direction: column;
                align-items: flex-start;
            }
            .week-selector select {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard QA - Análisis de Tarjetas</h1>
            <p class="timestamp">Generado el: """ + datetime.now().strftime('%d/%m/%Y a las %H:%M:%S') + """</p>
            <p class="timestamp">Total de semanas analizadas: """ + str(stats['total_weeks']) + """</p>
        </div>

        <div class="nav-tabs">
            <button class="tab-button active" onclick="showTab('resumen')">📈 Resumen General</button>
            <button class="tab-button" onclick="showTab('qa')">👥 QA</button>
            <button class="tab-button" onclick="showTab('web')">🌐 Web</button>
            <button class="tab-button" onclick="showTab('app')">📱 App</button>
            <button class="tab-button" onclick="showTab('devs')">👨‍💻 Desarrolladores</button>
            <button class="tab-button" onclick="showTab('pm')">📋 PM</button>
            <button class="tab-button" onclick="showTab('sites')">🏢 Sitios</button>
            <button class="tab-button" onclick="showTab('weekly')">📅 Vista Semanal</button>
        </div>

        <div id="resumen" class="tab-content active">
            <h2 class="section-title">Resumen General - Métricas Históricas</h2>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Tarjetas Revisadas</div>
                    <div class="stat-value">""" + str(stats['qa']['historical']['total_revisadas']) + """</div>
                    <p class="small-text">En """ + str(stats['total_weeks']) + """ semanas</p>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Total Rechazadas</div>
                    <div class="stat-value">""" + str(stats['qa']['historical']['total_rechazadas']) + """</div>
                    <p class="small-text">""" + str(round(stats['qa']['historical']['total_rechazadas'] / stats['qa']['historical']['total_revisadas'] * 100, 2) if stats['qa']['historical']['total_revisadas'] > 0 else 0) + """% del total</p>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Tarjetas Web</div>
                    <div class="stat-value">""" + str(stats['web']['historical']['total_revisadas']) + """</div>
                    <p class="small-text">""" + str(stats['web']['historical']['porcentaje_rechazo']) + """% rechazadas</p>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Tarjetas App</div>
                    <div class="stat-value">""" + str(stats['app']['historical']['total_revisadas']) + """</div>
                    <p class="small-text">""" + str(stats['app']['historical']['porcentaje_rechazo']) + """% rechazadas</p>
                </div>
            </div>

            <div class="chart-container">
                <div id="summaryChart"></div>
            </div>

            <h3 class="section-title">Distribución por Plataforma</h3>
            <div class="chart-container">
                <div id="platformChart"></div>
            </div>
        </div>

        <div id="qa" class="tab-content">
            <h2 class="section-title">Estadísticas Completas de QA</h2>

            <div class="info-box">
                <h3>📊 Resumen Histórico de QA</h3>
                <p><strong>Total de tarjetas revisadas:</strong> """ + str(stats['qa']['historical']['total_revisadas']) + """</p>
                <p><strong>Total de tarjetas rechazadas:</strong> """ + str(stats['qa']['historical']['total_rechazadas']) + """</p>
            </div>

            <h3>Detalle por QA (Histórico)</h3>
            <table>
                <thead>
                    <tr>
                        <th>QA/PM</th>
                        <th>Total Revisadas</th>
                        <th>Total Rechazadas</th>
                        <th>Promedio Semanal</th>
                        <th>% Rechazo</th>
                    </tr>
                </thead>
                <tbody>"""

        # Agregar datos de QA
        for qa, data in stats['qa']['historical']['por_qa'].items():
            porcentaje_rechazo = round((data['total_rechazadas'] / data['total_revisadas'] * 100) if data['total_revisadas'] > 0 else 0, 2)
            percentage_class = 'high' if porcentaje_rechazo > 20 else 'medium' if porcentaje_rechazo > 10 else 'low'
            html += f"""
                <tr>
                    <td data-label="QA/PM">{qa}</td>
                    <td data-label="Total Revisadas">{data['total_revisadas']}</td>
                    <td data-label="Total Rechazadas">{data['total_rechazadas']}</td>
                    <td data-label="Promedio Semanal">{data['promedio_semanal']:.2f}</td>
                    <td data-label="% Rechazo"><span class="percentage {percentage_class}">{porcentaje_rechazo}%</span></td>
                </tr>"""

        html += """
                </tbody>
            </table>

            <h3>Vista Semanal de QA</h3>
            <div class="week-selector">
                <label>Seleccionar semana: </label>
                <select id="qaWeekSelector" onchange="updateQAWeekView()">
                    <option value="all">Todas las semanas</option>"""

        for week in stats['weeks_list']:
            html += f'<option value="{week}">{week}</option>'

        html += """
                </select>
            </div>
            <div id="qaWeeklyDetails"></div>
        </div>

        <div id="web" class="tab-content">
            <h2 class="section-title">Estadísticas Completas Web</h2>

            <div class="metric-group">
                <h4>🌐 Totales Históricos Web</h4>
                <p><strong>Número de tarjetas revisadas:</strong> """ + str(stats['web']['historical']['total_revisadas']) + """</p>
                <p><strong>Número de tarjetas rechazadas:</strong> """ + str(stats['web']['historical']['total_rechazadas']) + """</p>
                <p><strong>Número de tarjetas aceptadas:</strong> """ + str(stats['web']['historical']['total_aceptadas']) + """</p>
                <p><strong>Porcentaje de rechazo:</strong> <span class="highlight">""" + str(stats['web']['historical']['porcentaje_rechazo']) + """%</span></p>
            </div>

            <h3>Estadísticas Web por Semana</h3>
            <table>
                <thead>
                    <tr>
                        <th>Semana</th>
                        <th>Revisadas</th>
                        <th>Aceptadas</th>
                        <th>Rechazadas</th>
                        <th>% Rechazo</th>
                    </tr>
                </thead>
                <tbody>"""

        # Datos semanales Web
        for week, data in stats['web']['weekly'].items():
            percentage_class = 'high' if data['porcentaje_rechazo'] > 20 else 'medium' if data['porcentaje_rechazo'] > 10 else 'low'
            html += f"""
                <tr>
                    <td data-label="Semana">{week}</td>
                    <td data-label="Revisadas">{data['revisadas']}</td>
                    <td data-label="Aceptadas">{data['aceptadas']}</td>
                    <td data-label="Rechazadas">{data['rechazadas']}</td>
                    <td data-label="% Rechazo"><span class="percentage {percentage_class}">{data['porcentaje_rechazo']}%</span></td>
                </tr>"""

        html += """
                </tbody>
            </table>

            <div class="chart-container">
                <div id="webTrendChart"></div>
            </div>
        </div>

        <div id="app" class="tab-content">
            <h2 class="section-title">Estadísticas Completas App</h2>

            <div class="metric-group">
                <h4>📱 Totales Históricos App</h4>
                <p><strong>Número de tarjetas revisadas:</strong> """ + str(stats['app']['historical']['total_revisadas']) + """</p>
                <p><strong>Número de tarjetas rechazadas:</strong> """ + str(stats['app']['historical']['total_rechazadas']) + """</p>
                <p><strong>Número de tarjetas aceptadas:</strong> """ + str(stats['app']['historical']['total_aceptadas']) + """</p>
                <p><strong>Porcentaje de rechazo:</strong> <span class="highlight">""" + str(stats['app']['historical']['porcentaje_rechazo']) + """%</span></p>
            </div>

            <h3>Estadísticas App por Semana</h3>
            <table>
                <thead>
                    <tr>
                        <th>Semana</th>
                        <th>Revisadas</th>
                        <th>Aceptadas</th>
                        <th>Rechazadas</th>
                        <th>% Rechazo</th>
                    </tr>
                </thead>
                <tbody>"""

        # Datos semanales App
        for week, data in stats['app']['weekly'].items():
            percentage_class = 'high' if data['porcentaje_rechazo'] > 20 else 'medium' if data['porcentaje_rechazo'] > 10 else 'low'
            html += f"""
                <tr>
                    <td data-label="Semana">{week}</td>
                    <td data-label="Revisadas">{data['revisadas']}</td>
                    <td data-label="Aceptadas">{data['aceptadas']}</td>
                    <td data-label="Rechazadas">{data['rechazadas']}</td>
                    <td data-label="% Rechazo"><span class="percentage {percentage_class}">{data['porcentaje_rechazo']}%</span></td>
                </tr>"""

        html += """
                </tbody>
            </table>

            <div class="chart-container">
                <div id="appTrendChart"></div>
            </div>
        </div>

        <div id="devs" class="tab-content">
            <h2 class="section-title">Estadísticas Completas de Desarrolladores</h2>

            <h3>🌐 Desarrollo Web - Todas las métricas</h3>
            <table>
                <thead>
                    <tr>
                        <th>Desarrollador</th>
                        <th>Total Tarjetas</th>
                        <th>Rechazadas</th>
                        <th>Aceptadas</th>
                        <th>Promedio Semanal (Histórico)</th>
                        <th>% Rechazo</th>
                        <th>Semanas Activo</th>
                    </tr>
                </thead>
                <tbody>"""

        # Top desarrolladores Web
        dev_count = 0
        for dev, data in stats['dev_web'].items():
            if dev_count < 20:  # Top 20
                percentage_class = 'high' if data['porcentaje_rechazo'] > 20 else 'medium' if data['porcentaje_rechazo'] > 10 else 'low'
                # Add ondblclick to the row
                html += f"""
                <tr class="developer-table-row" ondblclick="showDevWeeklyMetrics('{dev}', 'web')">
                    <td data-label="Desarrollador">{dev}</td>
                    <td data-label="Total Tarjetas">{data['total_tarjetas']}</td>
                    <td data-label="Rechazadas">{data['rechazadas']}</td>
                    <td data-label="Aceptadas">{data['aceptadas']}</td>
                    <td data-label="Promedio Semanal (Histórico)">{data['promedio_semanal_historico']}</td>
                    <td data-label="% Rechazo"><span class="percentage {percentage_class}">{data['porcentaje_rechazo']}%</span></td>
                    <td data-label="Semanas Activo">{data['semanas_activo']}</td>
                </tr>"""
                dev_count += 1

        html += """
                </tbody>
            </table>
            <div id="devWebWeeklyDetails" class="info-box" style="display: none;"></div>

            <h3>📱 Desarrollo App - Todas las métricas</h3>
            <table>
                <thead>
                    <tr>
                        <th>Desarrollador</th>
                        <th>Total Tarjetas</th>
                        <th>Rechazadas</th>
                        <th>Aceptadas</th>
                        <th>Promedio Semanal (Histórico)</th>
                        <th>% Rechazo</th>
                        <th>Semanas Activo</th>
                    </tr>
                </thead>
                <tbody>"""

        # Top desarrolladores App
        dev_count = 0
        for dev, data in stats['dev_app'].items():
            if dev_count < 20:  # Top 20
                percentage_class = 'high' if data['porcentaje_rechazo'] > 20 else 'medium' if data['porcentaje_rechazo'] > 10 else 'low'
                # Add ondblclick to the row
                html += f"""
                <tr class="developer-table-row" ondblclick="showDevWeeklyMetrics('{dev}', 'app')">
                    <td data-label="Desarrollador">{dev}</td>
                    <td data-label="Total Tarjetas">{data['total_tarjetas']}</td>
                    <td data-label="Rechazadas">{data['rechazadas']}</td>
                    <td data-label="Aceptadas">{data['aceptadas']}</td>
                    <td data-label="Promedio Semanal (Histórico)">{data['promedio_semanal_historico']}</td>
                    <td data-label="% Rechazo"><span class="percentage {percentage_class}">{data['porcentaje_rechazo']}%</span></td>
                    <td data-label="Semanas Activo">{data['semanas_activo']}</td>
                </tr>"""
                dev_count += 1

        html += """
                </tbody>
            </table>
            <div id="devAppWeeklyDetails" class="info-box" style="display: none;"></div>

            <div class="chart-container">
                <div id="devComparisonChart"></div>
            </div>
        </div>

        <div id="pm" class="tab-content">
            <h2 class="section-title">Estadísticas Completas de Project Management</h2>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Tarjetas Prioridad Alta</div>
                    <div class="stat-value">""" + str(stats['pm']['prioridades']['alta']['total']) + """</div>
                    <p class="small-text">Promedio: """ + str(stats['pm']['prioridades']['alta']['promedio_semanal']) + """ por semana</p>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Tarjetas Prioridad Media</div>
                    <div class="stat-value">""" + str(stats['pm']['prioridades']['media']['total']) + """</div>
                    <p class="small-text">Promedio: """ + str(stats['pm']['prioridades']['media']['promedio_semanal']) + """ por semana</p>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Tarjetas Prioridad Baja</div>
                    <div class="stat-value">""" + str(stats['pm']['prioridades']['baja']['total']) + """</div>
                    <p class="small-text">Promedio: """ + str(stats['pm']['prioridades']['baja']['promedio_semanal']) + """ por semana</p>
                </div>
            </div>

            <div class="metric-group">
                <h4>📊 Promedio de Tarjetas Enviadas por Semana</h4>
                <p><strong>Web:</strong> """ + str(stats['pm']['promedio_semanal']['web']) + """ tarjetas/semana</p>
                <p><strong>App:</strong> """ + str(stats['pm']['promedio_semanal']['app']) + """ tarjetas/semana</p>
                <p><strong>Total:</strong> """ + str(stats['pm']['promedio_semanal']['total']) + """ tarjetas/semana</p>
            </div>

            <h3>Desglose Semanal de Prioridades</h3>
            <table>
                <thead>
                    <tr>
                        <th>Semana</th>
                        <th>Alta</th>
                        <th>Media</th>
                        <th>Baja</th>
                        <th>Web</th>
                        <th>App</th>
                    </tr>
                </thead>
                <tbody>"""

        # Datos semanales PM
        for week, data in stats['pm']['por_semana'].items():
            html += f"""
                <tr>
                    <td data-label="Semana">{week}</td>
                    <td data-label="Alta">{data['alta']}</td>
                    <td data-label="Media">{data['media']}</td>
                    <td data-label="Baja">{data['baja']}</td>
                    <td data-label="Web">{data['web']}</td>
                    <td data-label="App">{data['app']}</td>
                </tr>"""

        html += """
                </tbody>
            </table>

            <div class="chart-container">
                <div id="priorityChart"></div>
            </div>
        </div>

        <div id="sites" class="tab-content">
            <h2 class="section-title">Estadísticas Completas por Sitio</h2>

            <table>
                <thead>
                    <tr>
                        <th>Sitio</th>
                        <th>Total</th>
                        <th>Web</th>
                        <th>App</th>
                        <th>Aceptadas</th>
                        <th>Rechazadas</th>
                        <th>Promedio/Semana</th>
                        <th>Promedio Rechazadas/Semana</th>
                        <th>Promedio Aceptadas/Semana</th>
                    </tr>
                </thead>
                <tbody>"""

        # Top sitios
        site_count = 0
        for site, data in stats['sites'].items():
            if site_count < 25:  # Top 25
                html += f"""
                <tr>
                    <td data-label="Sitio">{site}</td>
                    <td data-label="Total">{data['total']}</td>
                    <td data-label="Web">{data['web']}</td>
                    <td data-label="App">{data['app']}</td>
                    <td data-label="Aceptadas">{data['aceptadas']}</td>
                    <td data-label="Rechazadas">{data['rechazadas']}</td>
                    <td data-label="Promedio/Semana">{data['promedio_por_semana']}</td>
                    <td data-label="Promedio Rechazadas/Semana">{data['promedio_rechazadas_semana']}</td>
                    <td data-label="Promedio Aceptadas/Semana">{data['promedio_aceptadas_semana']}</td>
                </tr>"""
                site_count += 1

        html += """
                </tbody>
            </table>

            <div class="chart-container">
                <div id="siteChart"></div>
            </div>
        </div>

        <div id="weekly" class="tab-content">
            <h2 class="section-title">Vista Semanal Completa</h2>

            <div class="week-selector">
                <label>Seleccionar semana para análisis detallado: </label>
                <select id="weekSelector" onchange="updateWeeklyView()">"""

        for week in stats['weeks_list']:
            html += f'<option value="{week}">{week}</option>'

        html += """
                </select>
            </div>

            <div id="weeklyAnalysis"></div>
        </div>
    </div>

    <script>
        // Datos para los gráficos
        const allStats = """ + json.dumps(stats) + """;

        // Common Plotly layout options for consistency
        const commonLayout = {
            font: {
                family: 'Inter, sans-serif',
                size: 12,
                color: 'var(--text-dark)'
            },
            paper_bgcolor: 'var(--card-background)',
            plot_bgcolor: 'var(--card-background)',
            margin: { t: 60, b: 80, l: 60, r: 30 },
            hovermode: 'closest',
            title: {
                font: {
                    size: 18,
                    color: 'var(--text-dark)'
                },
                x: 0.05, // Align title to left
                xanchor: 'left'
            },
            xaxis: {
                showgrid: false,
                zeroline: false,
                linecolor: 'var(--border-light)',
                linewidth: 1,
                tickfont: { size: 10 }
            },
            yaxis: {
                showgrid: true,
                gridcolor: '#f0f0f0',
                zeroline: false,
                linecolor: 'var(--border-light)',
                linewidth: 1,
                tickfont: { size: 10 }
            },
            legend: {
                orientation: 'h',
                xanchor: 'center',
                x: 0.5,
                y: -0.2, // Below the chart
                font: { size: 10 }
            }
        };

        // Function to change tabs
        function showTab(tabName) {
            // Ocultar todos los tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));

            // Desactivar todos los botones
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(btn => btn.classList.remove('active'));

            // Mostrar tab seleccionado
            document.getElementById(tabName).classList.add('active');

            // Activar botón correspondiente
            const buttonTextMap = {
                'resumen': 'Resumen General',
                'qa': 'QA',
                'web': 'Web',
                'app': 'App',
                'devs': 'Desarrolladores',
                'pm': 'PM',
                'sites': 'Sitios',
                'weekly': 'Vista Semanal'
            };
            const clickedButton = Array.from(document.querySelectorAll('.tab-button')).find(btn => btn.textContent.includes(buttonTextMap[tabName]));
            if (clickedButton) {
                clickedButton.classList.add('active');
            }


            // Cargar gráficos según el tab
            if (tabName === 'resumen') {
                loadSummaryCharts();
            } else if (tabName === 'web') {
                loadWebCharts();
            } else if (tabName === 'app') {
                loadAppCharts();
            } else if (tabName === 'devs') {
                loadDevCharts();
                // Hide any previously shown developer weekly details
                document.getElementById('devWebWeeklyDetails').style.display = 'none';
                document.getElementById('devAppWeeklyDetails').style.display = 'none';
            } else if (tabName === 'pm') {
                loadPMCharts();
            } else if (tabName === 'sites') {
                loadSiteCharts();
            }
        }

        // Cargar gráficos de resumen
        function loadSummaryCharts() {
            // Gráfico de resumen general
            const summaryData = [
                {
                    x: ['Web', 'App'],
                    y: [allStats.web.historical.total_revisadas, allStats.app.historical.total_revisadas],
                    name: 'Total Revisadas',
                    type: 'bar',
                    marker: { color: 'var(--primary-color)' }
                },
                {
                    x: ['Web', 'App'],
                    y: [allStats.web.historical.total_rechazadas, allStats.app.historical.total_rechazadas],
                    name: 'Rechazadas',
                    type: 'bar',
                    marker: { color: 'var(--danger-color)' }
                },
                {
                    x: ['Web', 'App'],
                    y: [allStats.web.historical.total_aceptadas, allStats.app.historical.total_aceptadas],
                    name: 'Aceptadas',
                    type: 'bar',
                    marker: { color: 'var(--success-color)' }
                }
            ];

            const summaryLayout = {
                ...commonLayout,
                title: 'Resumen General - Web vs App',
                barmode: 'group',
                height: 400
            };

            Plotly.newPlot('summaryChart', summaryData, summaryLayout);

            // Gráfico de plataformas
            const platformData = {
                labels: Object.keys(allStats.platforms),
                values: Object.values(allStats.platforms),
                type: 'pie',
                hole: 0.4,
                textposition: 'outside', // Changed to outside for better readability
                textinfo: 'label+percent',
                marker: {
                    colors: [
                        '#4A00E0', '#8E2DE2', '#00C9FF', '#FF8C00', '#20B2AA',
                        '#FF6347', '#4682B4', '#DA70D6', '#3CB371', '#BA55D3'
                    ]
                },
                hoverinfo: 'label+value+percent',
                pull: [0.05, 0, 0, 0, 0, 0, 0, 0, 0, 0] // Slightly pull out the first slice
            };

            const platformLayout = {
                ...commonLayout,
                title: 'Distribución por Plataforma',
                height: 400,
                showlegend: true,
                legend: {
                    orientation: 'h',
                    xanchor: 'center',
                    x: 0.5,
                    y: -0.2, // Below the chart
                    font: { size: 10 }
                }
            };

            Plotly.newPlot('platformChart', [platformData], platformLayout);
        }

        // Cargar gráficos Web
        function loadWebCharts() {
            const weeks = Object.keys(allStats.web.weekly);
            const webData = Object.values(allStats.web.weekly);

            const webTrace = {
                x: weeks.map(w => w.replace('tarjetas semana ', '')),
                y: webData.map(d => d.porcentaje_rechazo),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Porcentaje de Rechazo',
                line: { color: 'var(--primary-color)', width: 3, shape: 'spline' },
                marker: { size: 8, symbol: 'circle', color: 'var(--primary-color)', line: { width: 1, color: 'white' } },
                hovertemplate: 'Semana: %{x}<br>Rechazo: %{y:.2f}%<extra></extra>'
            };

            const webLayout = {
                ...commonLayout,
                title: 'Tendencia de Rechazo Web por Semana',
                xaxis: { title: 'Semana' },
                yaxis: { title: 'Porcentaje de Rechazo (%)', range: [0, Math.max(...webData.map(d => d.porcentaje_rechazo)) * 1.2 || 100] },
                height: 400
            };

            Plotly.newPlot('webTrendChart', [webTrace], webLayout);
        }

        // Cargar gráficos App
        function loadAppCharts() {
            const weeks = Object.keys(allStats.app.weekly);
            const appData = Object.values(allStats.app.weekly);

            const appTrace = {
                x: weeks.map(w => w.replace('tarjetas semana ', '')),
                y: appData.map(d => d.porcentaje_rechazo),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Porcentaje de Rechazo',
                line: { color: 'var(--danger-color)', width: 3, shape: 'spline' },
                marker: { size: 8, symbol: 'square', color: 'var(--danger-color)', line: { width: 1, color: 'white' } },
                hovertemplate: 'Semana: %{x}<br>Rechazo: %{y:.2f}%<extra></extra>'
            };

            const appLayout = {
                ...commonLayout,
                title: 'Tendencia de Rechazo App por Semana',
                xaxis: { title: 'Semana' },
                yaxis: { title: 'Porcentaje de Rechazo (%)', range: [0, Math.max(...appData.map(d => d.porcentaje_rechazo)) * 1.2 || 100] },
                height: 400
            };

            Plotly.newPlot('appTrendChart', [appTrace], appLayout);
        }

        // Cargar gráficos de desarrolladores
        function loadDevCharts() {
            // Top 5 desarrolladores Web vs App
            const top5Web = Object.entries(allStats.dev_web).slice(0, 5);
            const top5App = Object.entries(allStats.dev_app).slice(0, 5);

            const traces = [
                {
                    x: top5Web.map(([dev, data]) => dev),
                    y: top5Web.map(([dev, data]) => data.total_tarjetas),
                    name: 'Web - Total',
                    type: 'bar',
                    marker: { color: 'var(--primary-color)' }
                },
                {
                    x: top5Web.map(([dev, data]) => dev),
                    y: top5Web.map(([dev, data]) => data.rechazadas),
                    name: 'Web - Rechazadas',
                    type: 'bar',
                    marker: { color: 'rgba(74, 0, 224, 0.6)' } // Lighter primary
                },
                {
                    x: top5App.map(([dev, data]) => dev),
                    y: top5App.map(([dev, data]) => data.total_tarjetas),
                    name: 'App - Total',
                    type: 'bar',
                    marker: { color: 'var(--danger-color)' }
                },
                {
                    x: top5App.map(([dev, data]) => dev),
                    y: top5App.map(([dev, data]) => data.rechazadas),
                    name: 'App - Rechazadas',
                    type: 'bar',
                    marker: { color: 'rgba(231, 76, 60, 0.6)' } // Lighter danger
                }
            ];

            const layout = {
                ...commonLayout,
                title: 'Top 5 Desarrolladores - Comparación Web vs App',
                barmode: 'group',
                height: 500,
                xaxis: { tickangle: -45 }
            };

            Plotly.newPlot('devComparisonChart', traces, layout);
        }

        // Cargar gráficos PM
        function loadPMCharts() {
            const weeks = Object.keys(allStats.pm.por_semana);
            const pmData = Object.values(allStats.pm.por_semana);

            const traces = [
                {
                    x: weeks.map(w => w.replace('tarjetas semana ', '')),
                    y: pmData.map(d => d.alta),
                    name: 'Alta',
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: { color: 'var(--danger-color)', width: 3, shape: 'spline' },
                    marker: { size: 8 }
                },
                {
                    x: weeks.map(w => w.replace('tarjetas semana ', '')),
                    y: pmData.map(d => d.media),
                    name: 'Media',
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: { color: 'var(--warning-color)', width: 3, shape: 'spline' },
                    marker: { size: 8 }
                },
                {
                    x: weeks.map(w => w.replace('tarjetas semana ', '')),
                    y: pmData.map(d => d.baja),
                    name: 'Baja',
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: { color: 'var(--success-color)', width: 3, shape: 'spline' },
                    marker: { size: 8 }
                }
            ];

            const layout = {
                ...commonLayout,
                title: 'Evolución de Prioridades por Semana',
                xaxis: { title: 'Semana' },
                yaxis: { title: 'Número de Tarjetas' },
                height: 400
            };

            Plotly.newPlot('priorityChart', traces, layout);
        }

        // Cargar gráficos de sitios
        function loadSiteCharts() {
            const top10Sites = Object.entries(allStats.sites).slice(0, 10);

            const traces = [
                {
                    x: top10Sites.map(([site, data]) => site),
                    y: top10Sites.map(([site, data]) => data.web),
                    name: 'Web',
                    type: 'bar',
                    marker: { color: 'var(--primary-color)' }
                },
                {
                    x: top10Sites.map(([site, data]) => site),
                    y: top10Sites.map(([site, data]) => data.app),
                    name: 'App',
                    type: 'bar',
                    marker: { color: 'var(--danger-color)' }
                }
            ];

            const layout = {
                ...commonLayout,
                title: 'Top 10 Sitios - Distribución Web vs App',
                barmode: 'stack',
                height: 400,
                xaxis: { tickangle: -45 }
            };

            Plotly.newPlot('siteChart', traces, layout);
        }

        // Actualizar vista semanal
        function updateWeeklyView() {
            const selectedWeek = document.getElementById('weekSelector').value;
            const weekData = {
                qa: allStats.qa.weekly[selectedWeek],
                web: allStats.web.weekly[selectedWeek],
                app: allStats.app.weekly[selectedWeek],
                pm: allStats.pm.por_semana[selectedWeek]
            };

            let html = '<div class="info-box">';
            html += '<h3>Resumen de ' + selectedWeek + '</h3>';
            html += '<div class="stats-grid">';
            html += '<div class="metric-group">';
            html += '<h4>QA</h4>';
            html += '<p>Total tarjetas: <strong>' + weekData.qa.total_semana + '</strong></p>';
            html += '<p>Total rechazadas: <strong>' + weekData.qa.total_rechazadas_semana + '</strong></p>';
            html += '</div>';
            html += '<div class="metric-group">';
            html += '<h4>Web</h4>';
            html += '<p>Revisadas: <strong>' + weekData.web.revisadas + '</strong></p>';
            html += '<p>Aceptadas: <strong>' + weekData.web.aceptadas + '</strong></p>';
            html += '<p>Rechazadas: <strong>' + weekData.web.rechazadas + '</strong></p>';
            html += '<p>% Rechazo: <span class="highlight">' + weekData.web.porcentaje_rechazo + '%</span></p>';
            html += '</div>';
            html += '<div class="metric-group">';
            html += '<h4>App</h4>';
            html += '<p>Revisadas: <strong>' + weekData.app.revisadas + '</strong></p>';
            html += '<p>Aceptadas: <strong>' + weekData.app.aceptadas + '</strong></p>';
            html += '<p>Rechazadas: <strong>' + weekData.app.rechazadas + '</strong></p>';
            html += '<p>% Rechazo: <span class="highlight">' + weekData.app.porcentaje_rechazo + '%</span></p>';
            html += '</div>';
            html += '<div class="metric-group">';
            html += '<h4>Prioridades</h4>';
            html += '<p>Alta: <strong>' + weekData.pm.alta + '</strong></p>';
            html += '<p>Media: <strong>' + weekData.pm.media + '</strong></p>';
            html += '<p>Baja: <strong>' + weekData.pm.baja + '</strong></p>';
            html += '</div>';
            html += '</div>';
            html += '</div>';

            document.getElementById('weeklyAnalysis').innerHTML = html;
        }

        // Actualizar vista semanal de QA
        function updateQAWeekView() {
            const selector = document.getElementById('qaWeekSelector');
            const selectedWeek = selector.value;

            if (selectedWeek === 'all') {
                document.getElementById('qaWeeklyDetails').innerHTML = '';
                return;
            }

            const weekData = allStats.qa.weekly[selectedWeek];
            let html = '<div class="info-box">';
            html += '<h4>Detalle de ' + selectedWeek + '</h4>';
            html += '<table><thead><tr><th>QA/PM</th><th>Tarjetas Revisadas</th><th>Tarjetas Rechazadas</th></tr></thead><tbody>';

            for (const [qa, count] of Object.entries(weekData.tarjetas_por_qa)) {
                const rechazadas = weekData.rechazadas_por_qa[qa] || 0;
                html += `<tr>
                            <td data-label="QA/PM">${qa}</td>
                            <td data-label="Tarjetas Revisadas">${count}</td>
                            <td data-label="Tarjetas Rechazadas">${rechazadas}</td>
                         </tr>`;
            }

            html += '</tbody></table></div>';
            document.getElementById('qaWeeklyDetails').innerHTML = html;
        }

        // NEW: Function to show weekly metrics for a specific developer
        function showDevWeeklyMetrics(developerName, devType) {
            let weeklyDetails = {};
            let targetDivId = '';

            if (devType === 'web') {
                weeklyDetails = allStats.dev_web_weekly_details[developerName];
                targetDivId = 'devWebWeeklyDetails';
            } else if (devType === 'app') {
                weeklyDetails = allStats.dev_app_weekly_details[developerName];
                targetDivId = 'devAppWeeklyDetails';
            }

            let html = `<h3>Métricas Semanales para ${developerName} (${devType.toUpperCase()})</h3>`;
            html += `<table>
                        <thead>
                            <tr>
                                <th>Semana</th>
                                <th>Total Tarjetas</th>
                                <th>Rechazadas</th>
                                <th>Aceptadas</th>
                                <th>% Rechazo</th>
                            </tr>
                        </thead>
                        <tbody>`;

            if (!weeklyDetails || Object.keys(weeklyDetails).length === 0) {
                html += `<tr><td colspan="5" style="text-align: center; color: var(--text-medium);">No hay datos semanales disponibles para este desarrollador.</td></tr>`;
            } else {
                for (const week of allStats.weeks_list) { // Iterate through all weeks to show gaps
                    const data = weeklyDetails[week];
                    if (data) {
                        const percentageClass = data.porcentaje_rechazo > 20 ? 'high' : (data.porcentaje_rechazo > 10 ? 'medium' : 'low');
                        html += `<tr>
                                    <td data-label="Semana">${week}</td>
                                    <td data-label="Total Tarjetas">${data.total_tarjetas}</td>
                                    <td data-label="Rechazadas">${data.rechazadas}</td>
                                    <td data-label="Aceptadas">${data.aceptadas}</td>
                                    <td data-label="% Rechazo"><span class="percentage ${percentageClass}">${data.porcentaje_rechazo}%</span></td>
                                </tr>`;
                    } else {
                        html += `<tr>
                                    <td data-label="Semana">${week}</td>
                                    <td colspan="4" style="text-align: center; color: var(--text-medium); font-style: italic;">(No activo esta semana)</td>
                                </tr>`;
                    }
                }
            }

            html += `</tbody></table>`;

            const targetDiv = document.getElementById(targetDivId);
            targetDiv.innerHTML = html;
            targetDiv.style.display = 'block'; // Make the div visible

            // Scroll to the new details section
            targetDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }


        // Cargar gráficos iniciales
        loadSummaryCharts();

        // Inicializar vista semanal con la primera semana
        if (allStats.weeks_list.length > 0) {
            document.getElementById('weekSelector').value = allStats.weeks_list[0];
            updateWeeklyView();
        }
    </script>
</body>
</html>"""

        return html

    def save_dashboard(self, filename='qa_dashboard_completo.html'):
        """Guarda el dashboard completo como archivo HTML"""
        print("\nGenerando todas las estadísticas...")
        stats = self.generate_all_statistics()

        print("Creando dashboard HTML completo...")
        html_content = self.generate_html_dashboard(stats)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Dashboard guardado exitosamente como '{filename}'")
            # Abre el archivo automáticamente en el navegador predeterminado
            webbrowser.open(f'file:///{os.path.abspath(filename)}')
        except Exception as e:
            print(f"Error al guardar o abrir el dashboard: {e}")

if __name__ == "__main__":
    try:
        dashboard = ComprehensiveQADashboard()
        dashboard.save_dashboard(filename="index.html")
    except FileNotFoundError:
        print("El archivo 'reporte_tarjetas.xlsx' no fue encontrado. Asegúrate de que esté en la misma carpeta que el script.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
