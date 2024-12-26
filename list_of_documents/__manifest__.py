{
    'name': 'List of Documents',
    'version': '16.0',
    'summary': 'List of Documents',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Forms',
    'depends': [
        'approval_portal',
        'approvals', 
        'approvals_position',
        'approvals_refused_reason',
        'proof_approval',
        'department_user', 
        'qhse_program', 
        'sequence_reset_period',
    ],
    'data': [
        'data/data.xml',
        'data/ir_sequence.xml',

        'security/ir.model.access.csv',
        
        'views/list_of_documents_views.xml',
        'views/amendment_document_views.xml',
    ],
    'auto_install': False,
    'application': False,
}