{
    'name': 'Report Sale Order',
    'version': '16.0',
    'summary': 'This module for print Report Sale Order for PT. Kokai Indo Abadi',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Report',
    'depends': [
        'crm_management',
        'sale',
        'report_py3o', 
    ],
    'data': [
        'views/sale_order_views.xml',
        'reports/reports.xml',
    ],
    'auto_install': False,
    'application': False,
}