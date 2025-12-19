{
    'name': 'Create product return, based on a previously issued Order',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': """Add a button in the Old Orders search section, which allows you to load a POS.order, with the same quantities but with a changed sign.
    It also adds additional information to the list view of the historical record, which is also searchable
    """,
    'category': 'Point of Sale',
    'live_test_url': 'https://www.ganemo.co/demo',
    'depends': [
        'point_of_sale', 
        'l10n_latam_invoice_document'
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_product_return/static/src/js/**/*',
            'pos_product_return/static/src/xml/**/*'
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
