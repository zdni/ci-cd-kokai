# Copyright 2014-2022 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Company Extension',
    'version': '16.0.1.0.0',
    'category': 'Partner',
    'license': 'AGPL-3',
    'summary': 'Adds capital and title on company',
    'author': 'Akretion',
    'website': 'https://github.com/akretion/odoo-usability',
    # I depend on base_usability only for _report_company_legal_name()
    'depends': ['base_usability'],
    'data': ['views/res_company.xml'],
    'installable': True,
}
