{
    'name': 'Activity Notes',
    'version': '16.0',
    'summary': 'This module enable User to create note in their activity',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Productivity',
    'depends': ['hr_timesheet', 'timesheet_grid', 'sale_timesheet_enterprise', 'mail'],
    'data': [
        'views/hr_timesheet_views.xml',
        'views/mail_activity_type_views.xml',
    ],
    'auto_install': False,
    'application': False,
}