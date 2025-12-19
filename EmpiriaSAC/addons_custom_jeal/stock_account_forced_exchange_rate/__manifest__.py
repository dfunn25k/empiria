# -*- coding: utf-8 -*-
{
    "name": "Stock Accounting - Forzar Tipo de Cambio",
    "summary": "Control avanzado del tipo de cambio en recepciones y valoración contable de inventario.",
    "description": """
        Gestión avanzada del tipo de cambio en valoración de stock.

        Este módulo extiende el comportamiento estándar de Odoo para permitir control total
        del tipo de cambio aplicado en recepciones de mercancía con moneda extranjera.

        Principales funcionalidades:
        ✓ **Fecha personalizada para el tipo de cambio**  
        Permite seleccionar una fecha distinta a la del movimiento para obtener la tasa 
        histórica del sistema (ejemplo: factura llega días después del ingreso físico).

        ✓ **Tipo de cambio forzado manualmente**  
        Permite ingresar un valor numérico exacto (DUA/DAM u otro documento aduanero).

        ✓ **Consistencia contable completa**  
        El asiento contable (`account.move`) refleja exactamente el tipo de cambio configurado,
        asegurando trazabilidad y auditoría coherente.

        ✓ **Valoración real en inventario (Kardex)**  
        Sobrescribe cálculo de `stock.valuation.layer` para asegurar que la valoración coincida
        matemáticamente con el tipo de cambio seleccionado o forzado.
    """,
    "author": "EMPIRIA",
    "website": "https://www.empiria.com",
    "category": "Inventory/Valuation",
    "version": "16.0.1.0.4",
    "license": "LGPL-3",
    "depends": [
        "stock",
        "stock_account",
        "purchase_stock",
        "account_field_to_force_exchange_rate",
        "account_forced_exchange_rate_extended",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
