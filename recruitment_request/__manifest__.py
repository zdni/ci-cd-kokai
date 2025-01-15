{
    'name': 'Recruitment Request',
    'version': '16.0',
    'summary': 'Recruitment Request by each Department',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': [
        'approval_portal',
        'hr_recruitment', 
        'department_user', 
        'department_detail',
        'approvals',
        'approvals_position',
        'approvals_refused_reason',
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

        'views/hr_allowance_views.xml',
        'views/recruitment_request_views.xml',
    ],
    'auto_install': False,
    'application': False,
}