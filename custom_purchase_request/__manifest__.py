{
    'name': 'Custom Purchase Request',
    'version': '16.0',
    'summary': 'This module add custom field for Purchase Request Document at PT. Kokai Indo Abadi',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Purchase',
    'depends': ['purchase_request', 'department_user', 'schedule_task', 'department_detail', 'company_director'],
    'data': [
        'data/data.xml',
        'data/purchase_request_type_data.xml',
        
        'security/ir.model.access.csv',

        'views/purchase_request_views.xml',
        'views/department_team_views.xml',
    ],
    'auto_install': False,
    'application': False,
}