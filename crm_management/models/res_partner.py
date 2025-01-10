from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    quadrant = fields.Selection([
        ('i', 'I'),
        ('ii', 'II'),
        ('iii', 'III'),
        ('iv', 'IV'),
    ], string='Quadrant', default='iv', required=True)