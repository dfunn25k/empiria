# -*- coding: utf-8 -*-
{
    "name": "l10n_pe_account_reten",
    "summary": "Módulo para la gestión de retenciones en Perú",
    "description": """
        Este módulo permite la gestión de retenciones en el sistema contable de Perú (Pe).
        Incluye funcionalidades para la emisión, configuración y control de retenciones.
        Compatible con Odoo 16.
    """,
    "author": "JEAL",
    "category": "Accounting",
    "version": "16.0.2.5.6",
    "website": "https://www.jeal.com",
    "depends": [
        "base",  # Módulo base de Odoo
        "contacts",  # Gestión de contactos
        "account",  # Gestión contable
        "account_accountant",  # Funciones avanzadas de contabilidad
        "l10n_latam_invoice_document",  # Localización para documentos de facturación en LATAM
    ],
    "license": "AGPL-3",
    "data": [
        # Archivos de seguridad y acceso
        "security/retention_security.xml",
        "security/ir.model.access.csv",
        # Vistas personalizadas y heredadas
        "views/res_config_settings_view.xml",  # Configuración en la vista de ajustes
        "views/res_partner_inh_view.xml",  # Herencia de la vista de res.partner
        "views/account_payment_inh_view.xml",
        "wizard/account_payment_register_inh_view.xml",
        "views/account_move_inh_view.xml",  # Herencia de la vista de account.move
        "views/account_move_line_inh_view.xml",  # Herencia de la vista de account.move.line
        "views/account_retention_main_view.xml",  # Vista principal de retenciones
        "views/account_retention_header_view.xml",  # Vista para los encabezados de retenciones
        "views/account_retention_tap_invoice_view.xml",  # Vista para el tap de facturas de retenciones
        "views/menuitems.xml",  # Definición de los menús del módulo
        # Datos de configuración inicial (carga de diario de retenciones)
        "data/account_journal_data.xml",
    ],
    "images": ["static/description/icon.jpg"],  # Imagen de ícono para la app
    "post_init_hook": "post_install_hook",  # Hook para ejecutar tras la instalación
    "installable": True,  # El módulo es instalable
    "application": False,  # No es una aplicación completa, sino un complemento
    "auto_install": False,  # No se instala automáticamente
}
