{
    'name': 'POS multi UOM product right',
    'version': '16.0.1.0.4',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co/',
    'summary': 'This module allows you to modify the unit of measure used in the sale of products at the point of sale.',
    'description': """
    This module allows you to modify the unit of measure used in the sale of products at the point of sale.
    """,
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos.xml',
        'views/product.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_multi_uom_product_right/static/src/js/**/*',
            'pos_multi_uom_product_right/static/src/xml/pos_multi_uom_button.xml',
            'pos_multi_uom_product_right/static/src/xml/pos_multi_uom_popup.xml',
        ]
    },

    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 39.90,
}
