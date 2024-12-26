{
    'name': 'Employee Overtime',
    'version': '16.0',
    'summary': 'Employee Overtime Request Form',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['hr', 'sequence_reset_period', 'approval_portal', 'approvals', 'approvals_position', 'approvals_refused_reason', 'proof_approval'],
    'data': [
        'data/approval_category_data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',

        'views/hr_overtime_views.xml',
    ],
    'auto_install': False,
    'application': False,
}