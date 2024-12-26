{
    'name': 'Attendance from Fingerprint',
    'version': '16.0',
    'summary': 'Get Attendance from Fingerprint use pyzk library',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['hr', 'portal', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',

        'views/fingerprint_device_views.xml',

        'reports/report.xml',

        'wizards/employee_attendance_wizard.xml',
    ],
    'auto_install': False,
    'application': False,
}