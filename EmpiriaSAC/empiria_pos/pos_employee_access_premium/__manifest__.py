{
    "name": "POS Employee Access",
    "version": "16.0.0.1.2",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/pos-employee-access-premium",
    "summary": "Set multiple pos permissions per employee",
    "description": """
    Allows employees to configure these permissions of the point of sale: 
    1- Access to Closing POS,
    2- Order Deletion, 
    3- Order Line Deletion, 
    4- Discount Application,
    5- Order Payment, 
    6- Price Change and 
    7- Decreasing Quantity
    """,
    "module_type":"official",
    "category": "Point of Sale",
    "depends": ["pos_hr"],
    "data": ["views/hr_employee_views.xml"],
    'assets': {
        'point_of_sale.assets': [
            'pos_employee_access_premium/static/src/js/**/*',
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 62.00,
}
