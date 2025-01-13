from odoo import _, api, fields, models


class ProductAsset(models.Model):
    _name = 'product.asset'
    _description = 'Product Asset'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name', required=True)