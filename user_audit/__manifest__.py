{
    'name': "User Activity Audit",
    "version": "16.0.1.0.0",
    "summary": "Tracking user's create, write, read activities",
    "description": "This module helps you to track user's all type of "
                    "activities like create, write, read etc on various models "
                    "and records in all users",
    "category": "Extra Tools",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['web'],
    'data': [
        'security/user_audit_groups.xml',
        'security/ir.model.access.csv',
        'data/user_audit_data.xml',
        'views/user_audit_log_views.xml',
        'views/user_audit_views.xml',
        'wizard/clear_user_log_views.xml',
        'views/user_audit_menus.xml'
    ],
    'assets':
        {
            'web.assets_backend': [
                'user_audit/static/src/js/list_controller.js',
                'user_audit/static/src/js/form_controller.js'
            ]},
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True
}
