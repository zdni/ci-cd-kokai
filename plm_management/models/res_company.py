from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    query_class = fields.Char('Query Class')
    query_size = fields.Char('Query Size')
    query_item = fields.Char('Query Item')