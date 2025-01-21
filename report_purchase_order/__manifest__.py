{
    'name': 'Report Purchase Order',
    'version': '16.0',
    'summary': 'This module for print Report Purchase Order for PT. Kokai Indo Abadi',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Report',
    'depends': ['purchase', 'report_py3o', 'approvals_purchase_order'],
    'data': [
        'views/purchase_order_views.xml',
        'reports/reports.xml',
    ],
    'auto_install': False,
    'application': False,
}