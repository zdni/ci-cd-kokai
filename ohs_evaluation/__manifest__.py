{
    'name': 'OHS Evaluation',
    'version': '16.0',
    'summary': '',
    'author': 'github.com/zdni',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'hr', 
        'calendar', 
        'survey',
        'sequence_reset_period',
        'schedule_task'
    ],
    'data': [
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/nonconformity_views.xml',
        'views/ohs_evaluation_views.xml',
        'views/survey_survey_views.xml',
    ],
    'auto_install': False,
    'application': False,
}