{
    'name': 'Exclude lines at zero in e-Fact',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'In the electronic invoice .xml, exclude invoice lines with total price equal to zero.',
    'description': """
        When preparing the .xml file that is sent to the electronic invoice validator (SUNAT or OSE), 
        exclude the lines whose total price of the invoice line is equal to zero.""",
    'category': 'Accounting',
    'depends': ['l10n_pe_edocument'],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 148.00
}