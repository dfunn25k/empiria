{
    'name': 'Manage combos at the point of sale',
    'version': '16.0.0.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'live_test_url': 'https://www.ganemo.co/demo',
    'summary': "Allows the management of Combos from the Point of Sale",
    'description': """
    You can create Combo type products, associated with several products. When you choose the "Combo", add, remove, through a dynamic selection, the items or
    products that make up the combo.
    """,
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_combo_reload/static/src/css/pos.css',
            'pos_combo_reload/static/src/js/**/*',
            'pos_combo_reload/static/src/xml/**/*'
        ]
    },
    "auto_install": False,
    "installable": True,
    'license': "Other proprietary",
    'currency': "USD",
    'price': 158,
}
