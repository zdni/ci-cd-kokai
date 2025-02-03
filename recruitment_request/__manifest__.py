{
    'name': 'Recruitment Request',
    'version': '16.0',
    'summary': 'Recruitment Request by each Department',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': [
        'approval_portal',
        'approvals',
        'approvals_position',
        'approvals_refused_reason',
        'department_detail',
        'department_user', 
        'hr_recruitment', 
        'hr_payroll_configuration',
        'minutes_of_meeting',
        'proof_approval',
        'schedule_task',
    ],
    'data': [
        'data/approval_category_data.xml',
        'data/data.xml',
        'security/group_security.xml',
        'security/ir_rules.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/hr_applicant_views.xml',
        'views/recruitment_request_views.xml',

        'wizards/schedule_meeting_wizard.xml',
    ],
    'auto_install': False,
    'application': False,
}