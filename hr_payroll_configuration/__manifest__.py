{
    'name': 'Payroll Configuration',
    'version': '16.0',
    'summary': 'Payroll Configuration',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['hr', 'department_user', 'hr_contract', 'account', 'hr_leave', 'opsway_2many_clickable_tag'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_allowance_views.xml',
    ],
    'auto_install': False,
    'application': False,
}