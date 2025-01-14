{
    'name': 'Inventory Adjustment Import',
    'version': '16.0',
    'summary': 'Import Inventory Adjustment',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/import_inventory_adjustment_wizards.xml'
    ],
    'auto_install': False,
    'application': False,
}