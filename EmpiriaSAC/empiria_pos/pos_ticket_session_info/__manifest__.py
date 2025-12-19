{
    "name": "Add information to the ticket printing format",
    "version": "16.0.0.2.3",
    "author": "Ganemo, Tiam-V S.A.C",
    "website": "https://www.ganemo.co/",
    "summary": "Adds information related to the point of sale, to the ticket printing format",
    "description": """
    Adds to the ticket printing format, information related to the point of sale.
    """,
    "category": "Point of Sale",
    "depends": ["pos_ticket_format_invoice"],
    "data": ["reports/ticket_template.xml"],
    "assets": {
        "web.report_assets_common": [
            "pos_ticket_session_info/static/src/css/main.css",
        ],
        'point_of_sale.assets': [
            'pos_ticket_session_info/static/src/js/**/*'
        ]
    },
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 45.00,
}
