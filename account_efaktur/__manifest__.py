{
    'name': 'Account E-Faktur Indonesia',
    'version': '16.0',
    'summary': 'Export Account Invoice for Upload in E-Faktur Indonesia',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'depends': ['account', 'stock', 'res_localization'],
    'data': [
        'data/parameters.xml',

        'security/ir.model.access.csv',

        'report/report_account_move.xml',

        'views/account_efaktur_views.xml',
        'views/account_move_views.xml',
        'views/product_template_views.xml',
        'views/res_partnet_views.xml',

        'wizards/assign_efaktur_wizard_views.xml',
        'wizards/auto_numbering_efaktur_wizard_views.xml',
        'wizards/generate_efaktur_wizard_views.xml',
    ],
    'auto_install': False,
    'application': False,
}