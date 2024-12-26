{
    'name': 'Price Query Form',
    'version': '16.0',
    'summary': 'Price Query Form to Request Specifications, Price and Drawing Sheet of Items in Lead',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': [
        'approval_portal',
        'approvals',
        'approvals_position',
        'approvals_refused_reason',
        'crm_management', 
        'engineering_aspects',
        'sale', 
        'sequence_reset_period',
        'schedule_task',
        'stock',
        'proof_approval', 
    ],
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/inquiry_review_views.xml',
        'views/price_query_views.xml',
    ],
    'auto_install': False,
    'application': False,
}