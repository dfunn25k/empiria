{
    'name': 'Set the reference of the rectified document in the POS',
    'version': '16.0.0.0.3',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Set the reference of the rectified document in the POS.',
    'category': 'Point of Sale',
    'depends': [
        'account_origin_invoice',
        'l10n_latam_invoice_document',
        'serie_and_correlative_pos',
        'pos_product_return'
    ],
    'data': [
        'views/pos_order_views.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_rectified_document_reference/static/src/scss/pos.scss',
            'pos_rectified_document_reference/static/src/js/**/*',
            'pos_rectified_document_reference/static/src/xml/**/*'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 120.00
}
