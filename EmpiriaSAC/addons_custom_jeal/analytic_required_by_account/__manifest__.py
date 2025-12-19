{
    "name": "Requerimiento Analítico por Cuenta",
    "version": "16.0.1.0.1",
    "category": "Accounting/Accounting",
    "summary": """
        Hace obligatoria la distribución analítica en líneas de factura y
        asientos contables si la cuenta contable está marcada como requerida.
    """,
    "author": "EMPIRIA",
    "website": "https://www.empiria.com",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_account_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
