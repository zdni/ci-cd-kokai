{
    'name': 'Hardness Testing',
    'version': '16.0',
    'summary': 'Hardness Testing in Quality Control for Product',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Quality',
    'depends': ['qhse_program', 'schedule_task', 'component_inspection', 'sequence_reset_period', 'hr', 'approvals'],
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/hardness_testing_views.xml',
        'views/stock_picking_views.xml',
    ],
    'auto_install': False,
    'application': False,
}