{
    'name': 'Receiving Planning',
    'version': '16.0',
    'summary': 'Planning for Receiving Product from PO',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'depends': ['stock', 'schedule_task', 'sequence_reset_period', 'department_detail'],
    'data': [
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/receiving_planning_views.xml'
    ],
    'auto_install': False,
    'application': False,
}