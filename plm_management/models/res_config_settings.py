from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    query_class = fields.Char('Query Class', related='company_id.query_class', readonly=False)
    query_size = fields.Char('Query Size', related='company_id.query_size', readonly=False)
    query_item = fields.Char('Query Item', related='company_id.query_item', readonly=False)