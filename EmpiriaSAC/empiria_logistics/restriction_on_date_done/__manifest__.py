# -*- coding: utf-8 -*-
{
    "name": "Fecha Efectiva en modo lectura",
    "summary": "Hace el campo 'Fecha de transferencia efectiva' (date_done) solo lectura en las transferencias.",
    "description": """
        Este módulo modifica el formulario de transferencia de inventario en Odoo 16,
        haciendo que el campo 'date_done' (Fecha de transferencia efectiva) sea siempre
        de solo lectura, sin importar el estado del documento.
        
        Compatible con Odoo 16. No afecta la lógica del backend, solo la interfaz.
    """,
    "author": "Sinetics",
    "website": "https://www.sinetics.com",
    "category": "Inventory",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "stock",  # Módulo de inventario
    ],
    "data": [
        "views/stock_picking_form_inherit.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
