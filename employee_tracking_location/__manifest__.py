{
    'name': 'Employee Tracking Location',
    'version': '16.0',
    'summary': 'Base Module Tracking Location of Employee with API Feature to Receive Data from External System',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': [
        'department_detail',
        'hr',
    ],
    'data': [
        # 'data/ir_sequence.xml',
        'security/ir.model.access.csv',

        'views/employee_tracking_location_views.xml',
    ],
    'auto_install': False,
    'application': False,
}