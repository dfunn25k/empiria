# -*- coding: utf-8 -*-
{
    "name": "Reporte de Ventas e Ingresos en Excel",
    "summary": """
        Generación de reportes personalizados de ventas e ingresos en formato Excel.
    """,
    "description": """
        Este módulo permite generar reportes de ventas e ingresos en formato Excel 
        con filtros personalizados. Incluye un asistente (wizard) para seleccionar 
        los criterios de generación y organiza los resultados en un archivo Excel 
        con un diseño profesional.
    """,
    "author": "SINETICS",
    "website": "https://www.sinetics.com",
    "category": "Accounting/Reporting",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "analytic",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_analytic_line_inh_views.xml",
        "wizards/sales_income_report_wizard_views.xml",
        "views/financial_reports_menuitem.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
