{
    'name': 'Detail Picking',
    'version': '16.0',
    'summary': 'Show all Stock Picking for a Purchase Order or Sale Order',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'depends': ['stock', 'purchase', 'sale', 'sale_management'],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'auto_install': False,
    'application': False,
}