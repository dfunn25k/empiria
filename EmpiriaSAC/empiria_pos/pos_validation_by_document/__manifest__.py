{
    "name": "Add additional validations to the point of sale",
    "version": "16.0.0.1.2",
    "author": "Ganemo",
    "website": "https://www.ganemo.co/",
    "summary": "Depending on the customer's document type, verify that the correct Document Type is being issued",
    "description": """
    For each type of Customer document, identify the additional validations you want to perform. Control what type of sales document to use depending on the
     type of customer document and much more.
    """,
    "module_type": "official",
    "category": "Point of Sale",
    "depends": [
        "point_of_sale",
        "serie_and_correlative_pos",
        "document_type_validation",
        "invoice_validation_by_document"
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_validation_by_document/static/src/js/PaymentScreen.js',
            'pos_validation_by_document/static/src/js/models.js'
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "currency": "USD",
    "price": 150.00,
}
