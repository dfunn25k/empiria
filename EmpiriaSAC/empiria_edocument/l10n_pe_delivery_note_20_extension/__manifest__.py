{
    'name': 'Peruvian - Electronic Delivery Note extension 2',
    'version': '16.0.1.3.5',
    'author': 'Ganemo',
    'license': 'Other proprietary',
    'website': 'https://www.ganemo.co',
    'description': "extend Odoo native functions for electronic waybill - sender.",
    'summary': 'extend Odoo native functions for electronic waybill - sender.',
    'category': 'Accounting',
    'depends': [
        'l10n_pe_delivery_note_20',
        'localization_menu'
    ],
    'module_type': 'official',
    'data': [
        'security/ir.model.access.csv',
        'data/edi_delivery_guide.xml',
        'data/port_catalog_data.xml',
        'data/airport_catalog_data.xml',
        'data/identification_code_tax_concept_data.xml',
        'views/stock_picking_views.xml',
        'views/port_catalog_views.xml',
        'views/airport_catalog_views.xml',
        'views/tariff_subheading_views.xml',
        'views/identification_code_tax_concept_views.xml',
        'views/product_template_views.xml'
    ],
    'currency': 'USD',
    'price': 150.00
}
