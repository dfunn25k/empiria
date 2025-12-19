{
    'name': 'POS billing journal',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Use Billing Journal and document types in POS',
    'category': 'Point of Sale',
    'depends': [
        'autocreate_pos_invoice',
        'l10n_latam_invoice_document'
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/pos_order_views.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'serie_and_correlative_pos/static/src/scss/pos.scss',
            'serie_and_correlative_pos/static/src/js/models.js',
            'serie_and_correlative_pos/static/src/js/PaymentScreen.js',
            'serie_and_correlative_pos/static/src/xml/PaymentScreen.xml'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 235.00
}
