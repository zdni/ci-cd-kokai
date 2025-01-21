from odoo import _, api, fields, models, http
from odoo.exceptions import ValidationError

import base64
import requests
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approver_id = fields.Many2one('res.users','Approver', copy=False, tracking=True)
    price_term = fields.Selection([
        ('include', 'Include PPN'),
        ('exclude', 'Exclude PPN'),
    ], string='Price Term', default='include', tracking=True)
    payment_terms = fields.Char('Payment Terms', tracking=True)
    contactperson_id = fields.Many2one('res.partner', string='Contact Person', tracking=True)
    received_id = fields.Many2one('res.users', string='Received By', tracking=True)

    def action_print_py3o(self):
        return self.env.ref("report_purchase_order.action_report_purchase_order_py3o").report_action(self, config=False)

    def _get_string_price_term(self):
        self.ensure_one()
        price_term = dict(self._fields['price_term'].selection).get(self.price_term)
        return price_term


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    size = fields.Char('Size')