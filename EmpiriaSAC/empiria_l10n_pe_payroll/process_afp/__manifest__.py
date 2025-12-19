{
    'name': 'Process AFP',
    'version': '16.0.0.0.2',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': "",
    'depends': [
        'hr_localization_menu',
        'types_system_pension',
        'employee_service',
        'identification_type_employee',
        'personal_information',
        'setting_rules_payroll'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/afp_interface_views.xml',
        'views/hr_salary_rule_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 131.00,
    'module_type': 'official'
}
