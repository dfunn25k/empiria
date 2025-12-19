{
    "name": "Pos Ticket Discount",
    "version": "16.0.1.0.3",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/",
    "summary": "This module allows you to add the discount to each line of the printed invoice receipt format.",
    "description": """
        This module allows you to add the discount to each line of the printed invoice receipt format.
    """,
    "category": "Point of Sale",
    "depends": [
        "pos_ticket_format_invoice",
    ],
    "data": ["reports/ticket_template.xml"],
    "assets": {
        "web.report_assets_common": [
            "pos_ticket_discount/static/src/css/main.css",
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 20.00,
}
