{
    "name": "Customer document type in pos",
    "version": "16.0.0.0.0",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/boost-pos-product-qty",
    "live_test_url": "https://www.ganemo.co/demo",
    "summary": "Choose type of document when creating clients from POS",
    "description": """
     Choose the type of document when creating customers from the POS, in addition, the customer information printed on the ticket will appear
    """,
    "category": "Point Of Sale",
    'depends': [
        'document_type_validation',
        'print_pos_customer'
    ],
    'assets': {
        'point_of_sale.assets': [
            'document_type_on_pos/static/src/js/*.js',
            'document_type_on_pos/static/src/xml/*.xml',
        ]
    },
    "auto_install": False,
    "installable": True,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 23.00,
}

