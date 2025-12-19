{
    'name': 'Peruvian - Electronic Delivery Note extension',
    'version': '16.0.1.9.11',
    'author': 'Ganemo',
    'license': 'Other proprietary',
    'module_type': 'official',
    'website': 'https://www.ganemo.co',
    'description': "extend Odoo native functions for electronic waybill - sender.",
    'summary': 'extend Odoo native functions for electronic waybill - sender.',
    'live_test_url': 'https://www.ganemo.co/demo',
    'category': 'Accounting',
    'depends': [
        'l10n_pe_edi_stock_20',
        'l10n_pe_delivery_note_ple',
        'third_parties_delivery',
        'tributary_address_extension',
        'invoice_type_document_extension',
    ],
    'data': [
        'data/edi_delivery_guide.xml',
        'views/stock_picking_views.xml',
        'views/report_deliveryslip.xml',
        'views/res_config_settings_views.xml'
    ],
    'currency': 'USD',
    'price': 150.00
}
