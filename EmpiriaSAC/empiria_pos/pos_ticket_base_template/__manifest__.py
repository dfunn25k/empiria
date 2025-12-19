{
    'name': 'POS ticket base template',
    'version': '16.0.3.0.5',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'POS ticket base template',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_ticket_base_template/static/src/js/*.js',
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
