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

        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            raise

    def clean_data(self):
        """Limpia y prepara los datos"""
        # Convertir fechas
        date_columns = ['Fecha tentativa  de validación por parte de QA', 'Fecha de Aprobación o Rechazo']
        for col in date_columns:
            if col in self.all_data.columns:
                self.all_data[col] = pd.to_datetime(self.all_data[col], errors='coerce')

        # Limpiar valores nulos
        self.all_data['Número de rechazos'] = pd.to_numeric(self.all_data['Número de rechazos'], errors='coerce').fillna(0)
        self.all_data['Aceptado/Rechazado'] = self.all_data['Aceptado/Rechazado'].fillna('PENDIENTE')

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
                'promedio_semanal': len(qa_data) / len(self.weeks_list)
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

    def get_dev_web_statistics_complete(self):
        """Estadísticas COMPLETAS de desarrolladores Web"""
        web_data = self.all_data[self.all_data['Web/App'] == 'Web']
        dev_stats = {}

        for dev in web_data['Desarrollador'].dropna().unique():
            dev_data = web_data[web_data['Desarrollador'] == dev]

            # Calcular estadísticas por semana
            weekly_counts = dev_data.groupby('Semana').size()
            promedio_semanal = weekly_counts.mean()

            total = len(dev_data)
            rechazadas = len(dev_data[dev_data['Aceptado/Rechazado'] == 'RECHAZADO'])
            aceptadas = len(dev_data[dev_data['Aceptado/Rechazado'] == 'APROBADO'])

            dev_stats[dev] = {
                'total_tarjetas': total,
                'rechazadas': rechazadas,
                'aceptadas': aceptadas,
                'promedio_semanal_historico': round(promedio_semanal, 2),
                'porcentaje_rechazo': round((rechazadas / total * 100) if total > 0 else 0, 2),
                'semanas_activo': len(weekly_counts)
            }

        # Ordenar por total de tarjetas
        dev_stats = dict(sorted(dev_stats.items(), key=lambda x: x[1]['total_tarjetas'], reverse=True))

        return dev_stats

    def get_dev_app_statistics_complete(self):
        """Estadísticas COMPLETAS de desarrolladores App"""
        app_data = self.all_data[self.all_data['Web/App'] == 'App']
        dev_stats = {}

        for dev in app_data['Desarrollador'].dropna().unique():
            dev_data = app_data[app_data['Desarrollador'] == dev]

            # Calcular estadísticas por semana
            weekly_counts = dev_data.groupby('Semana').size()
            promedio_semanal = weekly_counts.mean()

            total = len(dev_data)
            rechazadas = len(dev_data[dev_data['Aceptado/Rechazado'] == 'RECHAZADO'])
            aceptadas = len(dev_data[dev_data['Aceptado/Rechazado'] == 'APROBADO'])

            dev_stats[dev] = {
                'total_tarjetas': total,
                'rechazadas': rechazadas,
                'aceptadas': aceptadas,
                'promedio_semanal_historico': round(promedio_semanal, 2),
                'porcentaje_rechazo': round((rechazadas / total * 100) if total > 0 else 0, 2),
                'semanas_activo': len(weekly_counts)
            }

        # Ordenar por total de tarjetas
        dev_stats = dict(sorted(dev_stats.items(), key=lambda x: x[1]['total_tarjetas'], reverse=True))

        return dev_stats

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
        pm_stats['prioridades']['alta']['promedio_semanal'] = round(pm_stats['prioridades']['alta']['total'] / num_semanas, 2)
        pm_stats['prioridades']['media']['promedio_semanal'] = round(pm_stats['prioridades']['media']['total'] / num_semanas, 2)
        pm_stats['prioridades']['baja']['promedio_semanal'] = round(pm_stats['prioridades']['baja']['total'] / num_semanas, 2)

        # Promedios por tipo
        web_por_semana = self.all_data[self.all_data['Web/App'] == 'Web'].groupby('Semana').size()
        app_por_semana = self.all_data[self.all_data['Web/App'] == 'App'].groupby('Semana').size()

        pm_stats['promedio_semanal']['web'] = round(web_por_semana.mean(), 2)
        pm_stats['promedio_semanal']['app'] = round(app_por_semana.mean(), 2)
        pm_stats['promedio_semanal']['total'] = round((web_por_semana.mean() + app_por_semana.mean()), 2)

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

        stats = {
            'qa': self.get_qa_statistics_complete(),
            'web': self.get_web_statistics_complete(),
            'app': self.get_app_statistics_complete(),
            'dev_web': self.get_dev_web_statistics_complete(),
            'dev_app': self.get_dev_app_statistics_complete(),
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
    <title>Dashboard QA Completo - Todas las Métricas</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f0f2f5;
            color: #1c1e21;
            line-height: 1.6;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .timestamp {
            opacity: 0.9;
            font-size: 0.9em;
        }

        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .tab-button {
            padding: 12px 24px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .tab-button:hover {
            background: #f5f5f5;
            transform: translateY(-2px);
        }

        .tab-button.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
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
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 10px 0;
        }

        .stat-label {
            color: #65676b;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .section-title {
            font-size: 1.8em;
            color: #1c1e21;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }

        table {
            width: 100%;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }

        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }

        tr:hover {
            background-color: #f8f9fa;
        }

        tr:last-child td {
            border-bottom: none;
        }

        .percentage {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85em;
        }

        .percentage.high {
            background-color: #fee;
            color: #d00;
        }

        .percentage.medium {
            background-color: #fff3cd;
            color: #856404;
        }

        .percentage.low {
            background-color: #d4edda;
            color: #155724;
        }

        .chart-container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }

        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }

        .metric-group {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        }

        .metric-group h4 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .week-selector {
            margin: 20px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .week-selector select {
            padding: 8px 15px;
            font-size: 1em;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            background: white;
            cursor: pointer;
        }

        .highlight {
            background: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }

        .small-text {
            font-size: 0.85em;
            color: #65676b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard QA Completo - Análisis de Tarjetas</h1>
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
                    <p class="small-text">""" + str(round(stats['qa']['historical']['total_rechazadas'] / stats['qa']['historical']['total_revisadas'] * 100, 2)) + """% del total</p>
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
                    <td>{qa}</td>
                    <td>{data['total_revisadas']}</td>
                    <td>{data['total_rechazadas']}</td>
                    <td>{data['promedio_semanal']:.2f}</td>
                    <td><span class="percentage {percentage_class}">{porcentaje_rechazo}%</span></td>
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
                <h4>📊 Totales Históricos Web</h4>
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
                    <td>{week}</td>
                    <td>{data['revisadas']}</td>
                    <td>{data['aceptadas']}</td>
                    <td>{data['rechazadas']}</td>
                    <td><span class="percentage {percentage_class}">{data['porcentaje_rechazo']}%</span></td>
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
                    <td>{week}</td>
                    <td>{data['revisadas']}</td>
                    <td>{data['aceptadas']}</td>
                    <td>{data['rechazadas']}</td>
                    <td><span class="percentage {percentage_class}">{data['porcentaje_rechazo']}%</span></td>
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
                html += f"""
                <tr>
                    <td>{dev}</td>
                    <td>{data['total_tarjetas']}</td>
                    <td>{data['rechazadas']}</td>
                    <td>{data['aceptadas']}</td>
                    <td>{data['promedio_semanal_historico']}</td>
                    <td><span class="percentage {percentage_class}">{data['porcentaje_rechazo']}%</span></td>
                    <td>{data['semanas_activo']}</td>
                </tr>"""
                dev_count += 1

        html += """
                </tbody>
            </table>

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
                html += f"""
                <tr>
                    <td>{dev}</td>
                    <td>{data['total_tarjetas']}</td>
                    <td>{data['rechazadas']}</td>
                    <td>{data['aceptadas']}</td>
                    <td>{data['promedio_semanal_historico']}</td>
                    <td><span class="percentage {percentage_class}">{data['porcentaje_rechazo']}%</span></td>
                    <td>{data['semanas_activo']}</td>
                </tr>"""
                dev_count += 1

        html += """
                </tbody>
            </table>

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
                    <td>{week}</td>
                    <td>{data['alta']}</td>
                    <td>{data['media']}</td>
                    <td>{data['baja']}</td>
                    <td>{data['web']}</td>
                    <td>{data['app']}</td>
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
                    <td>{site}</td>
                    <td>{data['total']}</td>
                    <td>{data['web']}</td>
                    <td>{data['app']}</td>
                    <td>{data['aceptadas']}</td>
                    <td>{data['rechazadas']}</td>
                    <td>{data['promedio_por_semana']}</td>
                    <td>{data['promedio_rechazadas_semana']}</td>
                    <td>{data['promedio_aceptadas_semana']}</td>
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

        // Función para cambiar tabs
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
            event.target.classList.add('active');

            // Cargar gráficos según el tab
            if (tabName === 'resumen') {
                loadSummaryCharts();
            } else if (tabName === 'web') {
                loadWebCharts();
            } else if (tabName === 'app') {
                loadAppCharts();
            } else if (tabName === 'devs') {
                loadDevCharts();
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
                    marker: { color: '#667eea' }
                },
                {
                    x: ['Web', 'App'],
                    y: [allStats.web.historical.total_rechazadas, allStats.app.historical.total_rechazadas],
                    name: 'Rechazadas',
                    type: 'bar',
                    marker: { color: '#e74c3c' }
                },
                {
                    x: ['Web', 'App'],
                    y: [allStats.web.historical.total_aceptadas, allStats.app.historical.total_aceptadas],
                    name: 'Aceptadas',
                    type: 'bar',
                    marker: { color: '#27ae60' }
                }
            ];

            const summaryLayout = {
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
                textposition: 'inside',
                textinfo: 'label+percent'
            };

            const platformLayout = {
                title: 'Distribución por Plataforma',
                height: 400
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
                line: { color: '#667eea', width: 3 },
                marker: { size: 8 }
            };

            const webLayout = {
                title: 'Tendencia de Rechazo Web por Semana',
                xaxis: { title: 'Semana' },
                yaxis: { title: 'Porcentaje de Rechazo (%)' },
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
                line: { color: '#e74c3c', width: 3 },
                marker: { size: 8 }
            };

            const appLayout = {
                title: 'Tendencia de Rechazo App por Semana',
                xaxis: { title: 'Semana' },
                yaxis: { title: 'Porcentaje de Rechazo (%)' },
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
                    marker: { color: '#667eea' }
                },
                {
                    x: top5Web.map(([dev, data]) => dev),
                    y: top5Web.map(([dev, data]) => data.rechazadas),
                    name: 'Web - Rechazadas',
                    type: 'bar',
                    marker: { color: '#a5b4fc' }
                },
                {
                    x: top5App.map(([dev, data]) => dev),
                    y: top5App.map(([dev, data]) => data.total_tarjetas),
                    name: 'App - Total',
                    type: 'bar',
                    marker: { color: '#e74c3c' }
                },
                {
                    x: top5App.map(([dev, data]) => dev),
                    y: top5App.map(([dev, data]) => data.rechazadas),
                    name: 'App - Rechazadas',
                    type: 'bar',
                    marker: { color: '#f1948a' }
                }
            ];

            const layout = {
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
                    line: { color: '#e74c3c' }
                },
                {
                    x: weeks.map(w => w.replace('tarjetas semana ', '')),
                    y: pmData.map(d => d.media),
                    name: 'Media',
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: { color: '#f39c12' }
                },
                {
                    x: weeks.map(w => w.replace('tarjetas semana ', '')),
                    y: pmData.map(d => d.baja),
                    name: 'Baja',
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: { color: '#27ae60' }
                }
            ];

            const layout = {
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
                    marker: { color: '#667eea' }
                },
                {
                    x: top10Sites.map(([site, data]) => site),
                    y: top10Sites.map(([site, data]) => data.app),
                    name: 'App',
                    type: 'bar',
                    marker: { color: '#e74c3c' }
                }
            ];

            const layout = {
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
            html += '<p>Total tarjetas: ' + weekData.qa.total_semana + '</p>';
            html += '<p>Total rechazadas: ' + weekData.qa.total_rechazadas_semana + '</p>';
            html += '</div>';
            html += '<div class="metric-group">';
            html += '<h4>Web</h4>';
            html += '<p>Revisadas: ' + weekData.web.revisadas + '</p>';
            html += '<p>Aceptadas: ' + weekData.web.aceptadas + '</p>';
            html += '<p>Rechazadas: ' + weekData.web.rechazadas + '</p>';
            html += '<p>% Rechazo: ' + weekData.web.porcentaje_rechazo + '%</p>';
            html += '</div>';
            html += '<div class="metric-group">';
            html += '<h4>App</h4>';
            html += '<p>Revisadas: ' + weekData.app.revisadas + '</p>';
            html += '<p>Aceptadas: ' + weekData.app.aceptadas + '</p>';
            html += '<p>Rechazadas: ' + weekData.app.rechazadas + '</p>';
            html += '<p>% Rechazo: ' + weekData.app.porcentaje_rechazo + '%</p>';
            html += '</div>';
            html += '<div class="metric-group">';
            html += '<h4>Prioridades</h4>';
            html += '<p>Alta: ' + weekData.pm.alta + '</p>';
            html += '<p>Media: ' + weekData.pm.media + '</p>';
            html += '<p>Baja: ' + weekData.pm.baja + '</p>';
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
                html += '<tr><td>' + qa + '</td><td>' + count + '</td><td>' + rechazadas + '</td></tr>';
            }

            html += '</tbody></table></div>';
            document.getElementById('qaWeeklyDetails').innerHTML = html;
        }

        // Cargar gráficos iniciales
        loadSummaryCharts();

        // Inicializar vista semanal con la primera semana
        if (allStats.weeks_list.length > 0) {
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