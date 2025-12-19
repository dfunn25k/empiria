{
    'name': "Check RUC and DNI from the POS",
    "version": '16.0.0.0.2',
    'author': 'Ganemo',
    'live_test_url': 'https://www.ganemo.co/demo',
    'website': 'https://www.ganemo.co',
    'summary': 'Consultation and autocompletion of RUC and DNI from the POS.',
    'category': "Point Of Sale",
    'depends': [
        'ruc_validation_sunat',
        'document_type_on_pos',
    ],
    'assets': {
        'point_of_sale.assets': [
            'ruc_validation_pos_sunat/static/src/js/pos_extended.js',
            'ruc_validation_pos_sunat/static/src/xml/**/*'
        ],
    },
    'auto_install': False,
    'installable': True,
    'license': "Other proprietary",
    'currency': "USD",
    'price': 99.00
}
