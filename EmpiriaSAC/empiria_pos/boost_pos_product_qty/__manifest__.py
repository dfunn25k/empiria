{
    "name": "Show product quantity in pos",
    "version": "16.0.0.2.2",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/boost-pos-product-qty",
    "summary": "Shows the quantities available from stock at the POS",
    "module_type": "official",
    "description": """
    Shows the quantities available from stock at the point of sale (POS)
    """,
    "category": "Point Of Sale",
    "depends": ['point_of_sale', 'stock'],
    'assets': {
        'point_of_sale.assets': [
            'boost_pos_product_qty/static/src/js/models.js',
            'boost_pos_product_qty/static/src/css/pos.css',
            'boost_pos_product_qty/static/src/xml/pos.xml'
        ]
    },
    "auto_install": False,
    "installable": True,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 32.00,
    "module_type": "official"
}
