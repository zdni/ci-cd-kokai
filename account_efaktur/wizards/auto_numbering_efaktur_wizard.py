from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AutoNumberingEFakturWizard(models.TransientModel):
    _name = 'auto.numbering.efaktur.wizard'
    
    start_date = fields.Date("Invoice Date Start", required=True)
    end_date = fields.Date("Invoice Date End", required=True)
    invoice_ids = fields.Many2many('account.move', string='Invoices')

    def confirm_button(self):
        self.ensure_one()
        efaktur_ids = self.env['account.efaktur'].search([('is_used','=',False)], order="name ASC")
        efaktur_len = len(efaktur_ids)

        i = 0
        for invoice in self.invoice_ids:
            if i >= efaktur_len:
                break
            invoice.efaktur_id = efaktur_ids[i]
            i+=1

        self.env.cr.commit()
        raise UserError("Auto Numbering E-Faktur for %s Invoices(s) is Finish!" % i)

    def find_invoices(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('invoice_date','>=', self.start_date),
            ('invoice_date','<=', self.end_date),
            ('state','=','open'),
            ('efaktur_id','=',False),
            ('move_type','=','out_invoice')
        ])
        invoice_ids = []
        for invoice in invoices:
            invoice_ids.append((4,invoice.id))

        self.invoice_ids = invoice_ids
        self.env.cr.commit()
        raise UserError("Found %s Invoices(s)!" % len(invoice_ids))

