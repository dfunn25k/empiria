{
    'name': 'Odoo POS Multi Currency',
    'version': '16.0.0.0.5',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'description': """
    This module is allow to pay with multiple currencies from POS Interface.    
    """,
    'summary': 'Payment with multiple currencies from Point of sale Interface',
    'category': 'Point of Sale',
    'depends': [
        'account',
        'point_of_sale',
        'web'
    ],
    'data': [
        'views/pos_config.xml',
        'data/no_res_currency_rate.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'boost_multi_currency_pos/static/src/css/main.css',
            'boost_multi_currency_pos/static/src/scss/pos.scss',
            'boost_multi_currency_pos/static/src/js/models.js',
            'boost_multi_currency_pos/static/src/js/PaymentScreen.js',
            'boost_multi_currency_pos/static/src/js/OrderReceipt.js',
            'boost_multi_currency_pos/static/src/js/CurrencyRateUpdatePopup.js',
            'boost_multi_currency_pos/static/src/xml/**/*'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 99.00,
    'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
    'module_type': 'official',
}
