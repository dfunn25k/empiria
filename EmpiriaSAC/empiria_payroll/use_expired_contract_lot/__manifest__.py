{
    'name': 'Use Expired Contracts in Batches',
    'version': '16.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'category': 'Human Resources',
    'summary': 'Calculate payroll batches for collaborators who no longer have a current contract. It is used, for example, to pay benefits for workers in some countries.',
    'description': '''Allows you to generate payroll batches including employees and contracts that are NOT working in the Calculation Period. 
        This is very useful when salary items must be paid to workers who have already been furloughed, for example, in the calculation of profits.
    ''',
    'depends': [
        'hr_payroll'
    ],
    'data': [
        'views/hr_payslip_run_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'module_type': 'official',
    'currency': 'USD',
    'price': 120.00
}
