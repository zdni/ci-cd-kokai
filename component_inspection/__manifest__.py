{
    'name': 'Component Inspection',
    'version': '16.0',
    'description': 'Component Inspection',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Services',
    'depends': [
        'approvals', 
        'purchase', 
        'qhse_program', 
        'sale', 
        'schedule_task',
        'stock', 
    ],
    'data': [
        'data/approval_category_data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/approval_inspection_views.xml',
        'views/component_inspection_views.xml',
        'views/stock_picking_views.xml',
    ],
    'auto_install': False,
    'application': False,
}