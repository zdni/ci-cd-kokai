from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    agreement_id = fields.Many2one('purchase.agreement', string='Agreement')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    agreement_id = fields.Many2one('agreement.line', string='Agreement')