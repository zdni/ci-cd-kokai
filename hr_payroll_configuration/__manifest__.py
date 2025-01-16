{
    'name': 'Payroll Configuration',
    'version': '16.0',
    'summary': 'Payroll Configuration',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_allowance_views.xml',
    ],
    'auto_install': False,
    'application': False,
}