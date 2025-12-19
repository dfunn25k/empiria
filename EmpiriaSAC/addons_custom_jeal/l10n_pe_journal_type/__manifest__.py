{
    'name': 'Peru - Tipo De Diario',
    'version': '16.0.1.0.0',
    'author': 'Odoo Company',
    'company': 'Odoo Company',
    'maintainer': 'Odoo Company',
    'summary': 'Campo en el diario para determinar si el diario contiene asientos de movimiento, apertura o cierre',
    'description': """
Este módulo crea un campo en el diario para determinar si el 
diario contiene asientos de movimiento, apertura o cierre.
""",
    'category': 'Accounting/Localizations',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_journal_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
}
