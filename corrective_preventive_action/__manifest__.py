{
    'name': 'Corrective and Preventive Action',
    'version': '16.0',
    'summary': 'Module for Report and Summary of Corrective and Preventive Action',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'DDC',
    'depends': [
        'approval_portal',
        'approvals',
        'approvals_position',
        'approvals_refused_reason',
        'hr',
        'proof_approval',
        'qhse_program',
        'schedule_task',
        'sequence_reset_period',
        'engineering_aspects',
    ],
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/summary_cpar_views.xml',
    ],
    'auto_install': False,
    'application': False,
}