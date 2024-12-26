{
    'name': 'Tensile Testing',
    'version': '16.0',
    'summary': 'Tensile Testing Product for Quality Control',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Quality',
    'depends': ['qhse_program', 'schedule_task', 'component_inspection', 'sequence_reset_period', 'approvals'],
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/stock_picking_views.xml',
        'views/tensile_testing_views.xml'
    ],
    'auto_install': False,
    'application': False,
}