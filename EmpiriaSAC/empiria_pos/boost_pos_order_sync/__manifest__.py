{
    'name': 'Boost POS order sync',
    'version': '16.0.0.0.4',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'The POS user can synchronize one POS session with other so they can send quotations from one POS to another in case of multiple orders.',
    'category': 'Point of Sale',
    'depends': ['pos_loyalty'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/res_config_settings.xml',
        'views/pos_order.xml',
        'views/pos_quote_line.xml',
        'views/pos_quote.xml',
        'reports/pos_quote_report.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'boost_pos_order_sync/static/src/scss/pos.scss',
            'boost_pos_order_sync/static/src/js/**/*',
            'boost_pos_order_sync/static/src/xml/**/*'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 180.00
}
