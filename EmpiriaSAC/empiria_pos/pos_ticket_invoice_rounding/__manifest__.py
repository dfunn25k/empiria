{
    'name': 'POS Ticket Invoice Rounding',
    'version': '16.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co/',
    'summary': 'This module will create the rounding line on our sales receipt.',
    'description': """
This module will create the rounding line on our sales receipt. That is, there will be two scenarios:

When the "Cash Rounding" field is active, when printing the ticket the rounded amount must be reflected as on the invoice, that is:

    - SUB TOTAL: S/xx.xx
    - IGV: S/xx.xx
    - Rounding: S/xx.xx
    - Total: S/xx.xx

When the "Cash Rounding" field is deactivated, only the traditional lines will be reflected, that is:

    - SUB TOTAL: S/xx.xx
    - IGV: S/xx.xx
    - Total: S/xx.xx

    """,
    'category': 'Sales/Point of Sale',
    'depends': [
        'pos_ticket_format_invoice',
    ],
    'data': [
        'reports/ticket_template.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 20.00,
}
