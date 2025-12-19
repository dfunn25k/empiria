{
    "name": "Advance POS Receipt Boost",
    "author": "Ganemo",
    "version": "16.0.0.0.0",
    "price": 50,
    "currency": 'USD',
    "website": "https://www.ganemo.co",
    'summary': 'Advance POS Receipt Boost',
    "description": """
        This app help to add customer details, invoice number and barcode in pos receipt.
    """,
    "license": "Other proprietary",
    "depends": ['pos_extend_receipt_app'],
    'assets': {
        'point_of_sale.assets': [
            'pos_extend_receipt_boost/static/src/xml/pos.xml',
        ],              
    },
    "data": [
        'views/pos_js.xml',
    ],
    "auto_install": False,
    "installable": True,
    "category": "Point of Sale",
}