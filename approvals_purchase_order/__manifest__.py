{
    'name': 'Approvals Purchase Order',
    'version': '16.0',
    'summary': 'Request Approval Purchase Order',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': [
        'approval_portal',
        'approvals_position',
        'approvals_refused_reason', 
        'company_director', 
        'purchase', 
        'department_detail',
        'proof_approval',
        'schedule_task',
    ],
    'data': [
        'data/approval_category_data.xml',

        'views/approval_request_views.xml',
        'views/purchase_order_views.xml',
    ],
    'auto_install': False,
    'application': False,
}