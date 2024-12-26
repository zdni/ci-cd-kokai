{
    'name': 'Maintenance Order',
    'version': '16.0',
    'summary': 'Manage Request for All Maintenance',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Services',
    'depends': ['department_detail', 'department_user'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',

        'views/hr_department_views.xml',
        'views/maintenance_order_views.xml',
    ],
    'auto_install': False,
    'application': False,
}