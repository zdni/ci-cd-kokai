{
    'name': 'Department Detail',
    'version': '16.0',
    'summary': 'Department Detail, include Team, Detail and Etc.',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['hr', 'sequence_reset_period', 'department_user'],
    'data': [
        'security/group_security.xml',
        'security/ir_rules.xml',
        'data/data.xml',
        'security/ir.model.access.csv',

        'views/department_activity_views.xml',
        'views/hr_department_views.xml',
        'views/hr_job_views.xml',
        'views/hr_work_area_views.xml',
        'views/mail_activity_type_views.xml',
        'views/schedule_shift_views.xml',

        'wizards/generate_sequence_wizard.xml',
    ],
    'auto_install': False,
    'application': False,
}