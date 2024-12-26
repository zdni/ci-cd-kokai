from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class AssignEFakturWizard(models.TransientModel):
    _name = 'assign.efaktur.wizard'
    _description = 'Assign E-Faktur Wizard'

    def _get_active_invoices(self):
        if self._context.get('active_model') == 'account.move':
            return self._context.get('active_ids', False)
        return False
    
    invoice_ids = fields.Many2many(comodel_name="account.move", string="Invoices", required=True, default=_get_active_invoices)
    efaktur_id = fields.Many2one(comodel_name="account.efaktur", string="Nomor E-Faktur", required=False, )

    def confirm_button(self):
        self.ensure_one()
        for inv in self.invoice_ids:
            inv.efaktur_id = self.efaktur_id
        return {'type': 'ir.actions.act_window_close'}
