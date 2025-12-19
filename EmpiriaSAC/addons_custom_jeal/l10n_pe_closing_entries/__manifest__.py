# -*- coding: utf-8 -*-
{
    "name": "Asientos de Cierre Contable",
    "version": "16.0.0.1.2",
    "summary": "Genera asientos de cierre automático para cuentas contables.",
    "author": "SINETICS",
    "website": "https://www.sinetics.com",
    "category": "Accounting/Accounting",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_account_views.xml",
        "wizards/closing_entry_wizard_views.xml",
        "views/closing_entry_menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
