{
    'name': 'Work Accident',
    'version': '16.0',
    'summary': 'Form to Work Accident',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['qhse_program', 'approvals', 'department_detail'],
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/approval_request_views.xml',
        'views/work_accident_views.xml',
    ],
    'auto_install': False,
    'application': False,
}