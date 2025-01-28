{
    'name': 'Import Contract',
    'description': '',
    'summary': 'Import Contract of Employee in Indonesia',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr',
        'hr_payroll_configuration',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/hr_contract_import_wizards.xml',
    ],
    'auto_install': False,
    'application': False,
}