{
    'name': 'Asset Management',
    'version': '16.0',
    'summary': 'Asset Management',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'depends': [
        'helpdesk_maintenance',
        'hr', 
        'sequence_reset_period', 
        'schedule_task',
        'stock', 
    ],
    'data': [
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/asset_management_views.xml',
        'views/product_views.xml',
    ],
    'auto_install': False,
    'application': False,
}