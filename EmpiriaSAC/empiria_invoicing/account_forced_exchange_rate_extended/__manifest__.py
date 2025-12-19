{
    "name": "Account: Forced Exchange Rate Extended",
    "summary": "Permite aplicar y controlar tasas de cambio manuales en pagos, extractos bancarios.",
    "description": """
        Este módulo extiende la funcionalidad estándar de contabilidad en Odoo para permitir el uso de una **tasa de cambio forzada (manual)** en los siguientes procesos contables:\n\n

        ⚙️ **Mixin reutilizable (`exchange.rate.mixin`)**\n
        - Proporciona una estructura base para definir y calcular tasas de cambio.\n
        - Permite que cualquier modelo que lo herede calcule sus importes basados en una tasa personalizada.\n\n
        
        💸 **Pagos (`account.payment.register`)**\n
        - Permite seleccionar y aplicar manualmente una tasa de cambio al registrar un pago.\n
        - Esta tasa influye en los montos convertidos y puede reemplazar la tasa del sistema.\n
        - Detecta si todas las líneas pertenecen a la misma factura y propone automáticamente su tasa.\n\n

        🏦 **Extractos bancarios (`account.bank.statement.line`)**\n  
        - Permite recalcular automáticamente el importe contable usando la tasa de cambio forzada.\n
        - Sincroniza esta tasa con los asientos contables generados desde la línea de extracto.\n\n

        ✅ **Funcionalidades clave:**\n
        - Control preciso del tipo de cambio en escenarios con múltiples monedas.\n
        - Coherencia entre pagos, extractos bancarios y facturas en moneda extranjera.\n
        - Soporte completo para redondeo y lógica contable basada en tasa forzada.\n
        - Ideal para empresas que necesitan reflejar tipos de cambio contractuales o específicos en lugar del oficial del día.\n\n

        Este módulo es especialmente útil en países con volatilidad cambiaria o normativas que permiten tasas alternativas.
    """,
    "author": "SINETICS",
    "website": "https://www.sinetics.com",
    "category": "Accounting",
    "version": "16.0.0.2.2",
    "license": "LGPL-3",
    "depends": [
        "account",
        "account_accountant",
        "account_field_to_force_exchange_rate",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/account_payment_register_inh_view.xml",
        "views/account_bank_statement_line_inh_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
