{
    'name': 'Get Geolocation',
    'version': '16.0',
    'summary': 'This module for get geolocation from User current location',
    'author': 'github.com/zdni',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'assets': {
        'web.assets.backend': [
            'get_geolocation/src/static/js/form.js',
        ],
    },
    'auto_install': False,
    'application': False,
}