# -*- coding: utf-8 -*-
{
    "name": "l10n_pe_txt_reten",
    "summary": "Genera archivos TXT para la declaración de retenciones, integrándose con la contabilidad de Odoo.",
    "description": """
        Este módulo permite la generación de archivos en formato TXT para la declaración de retenciones, facilitando la integración con los sistemas contables y de cumplimiento normativo. 
        Incluye herramientas para exportar datos de retenciones y genera reportes en formato compatible con las normativas locales.
    """,
    "author": "JEAL",
    "website": "https://www.jeal.com",
    "category": "Contabilidad",
    "version": "16.0.1.2.3",
    "depends": [
        "base",
        "account",
        "l10n_pe_account_reten",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/retention_file_txt_view.xml",
        "views/menuitems.xml",
        "views/account_move_line_inh_view.xml",
        "data/sequence.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
