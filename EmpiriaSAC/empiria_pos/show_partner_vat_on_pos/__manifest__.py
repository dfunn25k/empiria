{
    'name': 'Show partner VAT on POS',
    'version': '16.0.0.0.1',
    'author': 'Ganemo',
    "website": "https://www.ganemo.co",
    "live_test_url": "https://www.ganemo.co/demo",
    "summary": "Displays the customer's identification number, in the POS customer list",
    "description": """
         Displays the customer's identification number, in the POS customer list. When searching by document number, 
         it makes it easier to identify the customer being searched for.
        """,
    "category": "Point Of Sale",
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale.assets': [
            'show_partner_vat_on_pos/static/src/xml/templates.xml',
        ]
    },
    "auto_install": False,
    "installable": True,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 23.00,
}
