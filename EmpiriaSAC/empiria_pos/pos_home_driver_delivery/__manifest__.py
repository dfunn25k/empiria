{
    'name': 'POS Home Delivery Order in Odoo',
    'version': '16.0.0.1.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Allow Home Delivery option to Point of sale orders in Odoo.',
    "live_test_url": "https://www.ganemo.co/demo",
    'module_type': 'official',
    'category': 'Point of Sale',
    'depends': ['point_of_sale', 'pos_restaurant'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/pos_delivery_view.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_home_driver_delivery/static/src/css/**/*',
            'pos_home_driver_delivery/static/src/js/**/*',
            'pos_home_driver_delivery/static/src/xml/**/*'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 48.00
}
