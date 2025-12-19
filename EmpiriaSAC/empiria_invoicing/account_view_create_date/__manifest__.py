# -*- coding: utf-8 -*-
{
    "name": "Contabilidad: Añadir Fecha de Creación",
    "summary": 'Añade el campo "Fecha de Creación" a la vista lista de facturas.',
    "description": """
        Este módulo simple y ligero modifica la vista lista (árbol) de las facturas (account.move)
        para hacer visible el campo estándar 'create_date' (Fecha de Creación).

        Esto permite a los usuarios ver y ordenar las facturas por la fecha exacta en que
        fueron creadas en el sistema, además de la fecha de la factura.
    """,
    "version": "16.0.0.1.2",
    "category": "Accounting/Accounting",
    "author": "SINETICS",
    "website": "https://www.sinetics.com",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_move_inh_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
