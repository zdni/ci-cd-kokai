{
    'name': 'Department of User',
    'version': '16.0',
    'summary': 'Department of User',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': [ 'hr', 'hr_grade' ],
    'data': [
        'security/ir.model.access.csv',

        'views/hr_employee_views.xml',
        'views/res_users_views.xml'
    ],
    'auto_install': False,
    'application': False,
}