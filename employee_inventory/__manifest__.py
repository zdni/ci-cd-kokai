{
    'name': 'Employee Inventory',
    'version': '16.0',
    'summary': 'Borrowing or Use of Inventory by Employees',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'stock', 
        'hr',
        'mail', 
        'department_detail',
    ],
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/hr_department_views.xml',
        'views/hr_employee_views.xml',
        'views/stock_equipment_views.xml',
    ],
    'auto_install': False,
    'application': False,
}