{
    'name': 'Fleet Usage',
    'version': '16.0',
    'summary': 'Form for Fleet Usage',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['approvals', 'fleet', 'stock', 'sequence_reset_period', 'schedule_task'],
    'data': [
        'data/approval_category_data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/fleet_usage_views.xml',
        'views/fleet_vehicle_views.xml',
    ],
    'auto_install': False,
    'application': False,
}