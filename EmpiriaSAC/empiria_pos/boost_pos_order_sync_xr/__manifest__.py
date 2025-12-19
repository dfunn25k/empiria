{
    'name': 'Boost POS order sync xr',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'The POS user can synchronize one POS session with other so they can send quotations from one POS to another in case of multiple orders.',
    'category': 'Point of Sale',
    'depends': ['pos_restaurant', 'boost_pos_order_sync'],
    'data': ['reports/pos_quote_report.xml'],
    'assets': {
        'point_of_sale.assets': [
            'boost_pos_order_sync_xr/static/src/scss/pos.scss',
            'boost_pos_order_sync_xr/static/src/js/**/*',
            'boost_pos_order_sync_xr/static/src/xml/**/*'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 180.00
}