{
    'name': 'Always generate an invoice at your POS odoo',
    'version': '16.0.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'You choose which journal will be used by checking the Invoice option and which journal will be used when the invoice option is not checked.',
    'description': """In the configuration of each point of sale, you choose which journal 
    will be used when checking the Invoice option and which journal will be used when the invoice option 
    is not checked, but in any case, an Invoice will always be generated for each sale in the POS.
    """,
    'category': 'Point of Sale',
    'depends': ['point_of_sale', 'pos_sale'],
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'autocreate_pos_invoice/static/src/js/**/*'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 70.00
}
