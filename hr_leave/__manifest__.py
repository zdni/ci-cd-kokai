{
    'name': 'HR Leave',
    'version': '16.0',
    'summary': 'Module for Management Leave of Employee',
    'author': 'github/com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr',
        'approvals',
        'approvals_position',
        'approvals_refused_reason',
        'proof_approval',
        'approval_portal',
        'schedule_task',
        'sequence_reset_period',
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/approval_category_data.xml',

        'views/hr_leave_views.xml',
    ],
    'auto_install': False,
    'application': False,
}