{
    'name': 'Request Product',
    'version': '16.0',
    'description': '',
    'summary': 'This Module add feature for User can Request create some Product to Warehouse Team',
    'author': 'github.com/zdni',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'depends': [ 'stock', 'department_detail', 'schedule_task', 'sequence_reset_period', 'purchase_request', ],
    'data': [
        'data/ir_sequence.xml',

        'security/group_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',

        'views/request_product_views.xml',
    ],
    'auto_install': False,
    'application': False,
}