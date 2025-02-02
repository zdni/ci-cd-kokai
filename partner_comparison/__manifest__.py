{
    'name': 'Partner Comparison',
    'version': '16.0',
    'summary': 'Partner Comparison in Purchase Flow',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Purchase',
    'depends': [
        'custom_purchase_request',
        'many2many_attachment_preview',
        'purchase', 
        'purchase_discount',
        'purchase_request', 
        'sequence_reset_period', 
        'schedule_task',
    ],
    'data': [
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/purchase_agreement_views.xml',
        'views/purchase_request_views.xml',
    ],
    'auto_install': False,
    'application': False,
}