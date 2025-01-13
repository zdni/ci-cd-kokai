{
    'name': 'PLM Management',
    'version': '16.0',
    'summary': 'PLM Management for Manufacturing in Production',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Productivity',
    'depends': ['mrp', 'schedule_task'],
    'data': [
        'data/ir_sequence_data.xml',

        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/machine_views.xml',
        'views/work_order_views.xml',
    ],
    'auto_install': False,
    'application': False,
}