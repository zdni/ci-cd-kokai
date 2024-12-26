{
    'name': 'Employee Attendance',
    'version': '16.0',
    'description': '',
    'summary': 'Employee Attendance Data',
    'author': 'github.com/zdni',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['hr'],
    'data': [
        'data/data.xml',

        'security/ir.model.access.csv',

        'views/employee_attendance_views.xml',
    ],
    'auto_install': False,
    'application': False,
}