from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import get_lang


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    def _default_supplier_id(self):
        partner = self.env['res.partner'].search([ ('is_default', '=', True) ])
        if partner:
            return partner.id

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=True,
        context={"res_partner_search_mode": "supplier"},
        default=_default_supplier_id
    )