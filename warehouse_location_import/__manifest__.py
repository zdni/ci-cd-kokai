{
    'name': 'Warehouse Location Import',
    'version': '16.0',
    'summary': 'Import Warehouse Location',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/import_warehouse_location_wizards.xml'
    ],
    'auto_install': False,
    'application': False,
}