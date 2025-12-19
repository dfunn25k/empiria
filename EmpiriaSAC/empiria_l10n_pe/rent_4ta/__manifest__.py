{
    'name': 'Renta de 4ta',
    'version': '16.0.0.3.4',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Allow issuing txt files of receipts for fees to declare in the Plame.',
    'description': 'Allow issuing txt files of receipts for fees to declare in the Plame.',
    'category': 'Payroll',
    'module_type': 'official',
    'depends': [
        'contacts',
        'account',
        'tributary_address_extension',
        'first_and_last_name',
        'l10n_pe_edi',
        'ple_purchase_book', 
        'l10n_pe_advance_global_discount',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/rent_4ta_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'post_init_hook': 'post_init_hook',
    'currency': 'USD',
    'module_type': 'official',
    'price': 0.00
}