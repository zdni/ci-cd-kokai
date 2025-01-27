from odoo import _, api, fields, models


class ListOfDocuments(models.Model):
    _inherit = 'list.of.documents'

    type_id = fields.Many2one('manufacturing.type', string='Type')