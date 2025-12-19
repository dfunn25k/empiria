{
    'name': 'Select invoice format from POS',
    'version': '16.0.3.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Select which invoice printing format will be used when issuing an Invoice from the Point of Sale.',
    'category': 'Point of Sale',
    'depends': [
        'account',
        'pos_ticket_base_template',
    ],
    'module_type': 'official',
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'select_invoice_format_pos/static/src/js/*.js',
            'select_invoice_format_pos/static/src/xml/*.xml'
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 45.00
}
