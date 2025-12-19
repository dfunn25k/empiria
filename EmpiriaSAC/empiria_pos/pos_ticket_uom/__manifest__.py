{
    "name": "pos ticket uom",
    "version": "16.0.1.0.2",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/",
    "summary": "This module allows you to add the unit of measure of sale, in each line of the printed format of the invoice receipt.",
    "description": """
    """,
    "category": "Point of Sale",
    "depends": [
        "pos_ticket_format_invoice",
    ],
    "data": ["reports/ticket_template.xml"],
    "assets": {
        "web.report_assets_common": [
            "pos_ticket_uom/static/src/css/main.css",
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 120.00,
}
