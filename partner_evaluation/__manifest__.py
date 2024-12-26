{
    'name': 'Partner Evaluation',
    'version': '16.0',
    'summary': 'Partner Evaluation by Quality Control',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Technical',
    'depends': ['qhse_program', 'approvals'],
    'data': [
        'data/data.xml',
        'data/ir_sequence_data.xml',

        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/approval_request_views.xml',
        'views/evaluation_template_views.xml',
        'views/partner_evaluation_views.xml',
        'views/res_partner_views.xml',

        'wizards/generate_evaluation_wizard.xml',
    ],
    'auto_install': False,
    'application': False,
}