{
    "name": "Employee certificate for employee",
    'version': '16.0.1.1.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'category': 'Payroll',
    'summary': 'This module enables the issuance of work certificates for employees',
    "description": """
    This module enables the issuance of work certificates for employees.
    """,
    'module_type': 'official',
    "depends": [
        'hr_payroll',
        'base',
        'employee_service',
        'payment_conditions',
        'additional_fields_voucher',
        'identification_type_employee',
        'personal_information'
    ],
    "data": [
        'views/certificate_view.xml',
        'report/certification_employee_report.xml',
        'report/certification_employee_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
