{
    'name': 'Engineering Aspects',
    'version': '16.0',
    'description': '',
    'summary': 'Engineering Aspects of Product & Variants',
    'author': 'github.com/zdni',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Manufacturing',
    'depends': ['sequence_reset_period', 'stock', 'sale', 'list_of_documents'],
    'data': [
        'data/data.xml',
        
        'security/ir.model.access.csv',

        'views/list_of_documents_views.xml',
        'views/menu.xml',
        'views/product_product_views.xml',
        'views/standard_specification.xml',
    ],
    'auto_install': False,
    'application': False,
}