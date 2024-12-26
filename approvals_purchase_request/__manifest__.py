{
    'name': 'Approvals - Purchase Request',
    'version': '16.0',
    'description': """
        This module adds to the Purchase Request to generate 
        Approval from Purchase Request
    """,
    'author': 'https://github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': [
        'approval_portal',
        'approvals_position',
        'approvals_refused_reason', 
        'company_director', 
        'custom_purchase_request', 
        'department_detail',
        'proof_approval',
        'schedule_task',
    ],
    'data': [
        'data/approval_category_data.xml',
        
        'views/approval_request_views.xml',
        'views/purchase_request_views.xml',
    ],
    'auto_install': False,
    'application': False,
}