from odoo import _, api, fields, models


class ProductPart(models.Model):
    _name = 'product.part'
    _description = 'Product Part'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True)