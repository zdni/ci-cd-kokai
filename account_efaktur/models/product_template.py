from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_efaktur_exported = fields.Boolean('Is E-Faktur Exported')
    date_efaktur_exported = fields.Datetime('E-Faktur Exported Date')