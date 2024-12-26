from odoo import _, api, fields, models


class AccountEfaktur(models.Model):
    _name = 'account.efaktur'
    _description = 'Account Efaktur'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('E-Faktur Number', required=True)
    year = fields.Integer('Year', required=True)
    invoice_ids = fields.One2many('account.move', 'efaktur_id', string='Invoices')
    invoice_count = fields.Integer('Invoice Count', compute='_compute_invoice_count', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)

    @api.depends('invoice_ids')
    def _used(self):
        for record in self:
            record.is_used = False
            if record.invoice_ids:
                record.is_used = True
            
    is_used = fields.Boolean('Is Used', compute='_used', store=True)