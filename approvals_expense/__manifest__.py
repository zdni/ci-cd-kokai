{
    'name': 'Approvals for Expense',
    'version': '16.0',
    'summary': 'Approval Request for Expense',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Expense',
    'depends': [
        'approval_portal',
        'approvals',
        'approvals_position',
        'approvals_refused_reason',
        'hr_expense',
        'proof_approval',
        'schedule_task',
    ],
    'data': [
        'data/approval_category_data.xml',
        'views/approval_request_views.xml',
        'views/hr_expense_views.xml',
    ],
    'auto_install': False,
    'application': False,
}