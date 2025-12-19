{
    "name": "Print customer data on POS Ticket",
    "version": "16.0.0.0.0",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/",
    "summary": "Choose type of document when creating clients from POS",
    "description": """
     In the printed ticket of the POS add the customer information
    """,
    "category": "Point of Sale",
    'depends': [
        'point_of_sale'
    ],
    'assets': {
        'point_of_sale.assets': [
            'print_pos_customer/static/src/css/styles.css',
            'print_pos_customer/static/src/xml/**/*',
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 0.00,
}
