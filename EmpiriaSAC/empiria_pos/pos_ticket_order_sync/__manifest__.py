{
    "name": "Use POS ticket format to print invoices",
    "version": "16.0.0.0.0",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/",
    "summary": "Send quotations from one POS to another.",
    "description": """
    Adds to the ticket printing format, information related to the origin point of sale.
    """,
    "category": "Point of Sale",
    "depends": [
        "pos_ticket_session_info",
        "boost_pos_order_sync",
    ],
    "data": [
        "reports/ticket_template.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 225.00,
}
