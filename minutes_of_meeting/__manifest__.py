{
    'name': 'Minutes of Meeting',
    'version': '16.0',
    'summary': 'Module Minutes of Meeting in Schedule',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Productivity',
    'depends': [
        'department_detail', 
        'employee_attendance',
        'many2many_attachment_preview',
        'schedule_task', 
    ],
    'data': [
        'data/data.xml',
        
        'security/ir.model.access.csv',

        'views/schedule_task_views.xml',
    ],
    'auto_install': False,
    'application': False,
}