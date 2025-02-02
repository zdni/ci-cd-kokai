{
    'name': 'Custom Purchase Request',
    'version': '16.0',
    'summary': 'This module add custom field for Purchase Request Document at PT. Kokai Indo Abadi',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Purchase',
    'depends': [
        'company_director',
        'department_detail', 
        'department_user', 
        'many2many_attachment_preview',
        'ps_binary_field_attachment_preview',
        'purchase_request', 
        'schedule_task', 
    ],
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