{
    'name': 'Asset Management',
    'version': '16.0',
    'summary': 'Asset Management',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'depends': [
        'hr', 
        'sequence_reset_period', 
        'schedule_task',
        'stock', 
    ],
    'data': [
        'data/ir_sequence.xml',
    ],
    'auto_install': False,
    'application': False,
}