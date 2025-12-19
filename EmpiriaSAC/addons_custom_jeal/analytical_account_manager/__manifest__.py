# -*- coding: utf-8 -*-
{
    "name": "Manejo de Cuentas Analiticas",
    "summary": """
        Insertar dentro de la pantalla de expediciones un campo asociado a las cuentas analíticas , debe viajar al asiento de la transacción
    """,
    "description": """
        Insertar dentro de la pantalla de expediciones un campo asociado a las cuentas analíticas , debe viajar al asiento de la transacción
    """,
    "author": "SINETICS",
    "website": "https://www.sinetics.com",
    "category": "Uncategorized",
    "version": "16.0.0.0.1",
    "depends": [
        "base",
        "stock",
        "stock_barcode",
    ],
    "data": [
        "views/stock_picking_type_inh_view.xml",
        "views/stock_picking_inh_view.xml",
        "views/stock_move_line_inh_view.xml",
    ],
}
