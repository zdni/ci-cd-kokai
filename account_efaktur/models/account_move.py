from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    efaktur_id = fields.Many2one('account.efaktur', string='Nomor Seri Faktur Pajak')
    is_efaktur_exported = fields.Boolean('Is E-Faktur Exported')
    date_efaktur_exported = fields.Datetime('E-Faktur Exported Date')

    tax_period = fields.Char('Tax Period', compute='_compute_tax_period', store=True)
    tax_year = fields.Char('Tax Year', compute='_compute_tax_year', store=True)

    efaktur_input = fields.Char('Nomor Seri Faktur Pajak')
    is_union = fields.Boolean('Kawasan Berserikat?', related='partner_id.is_union')
    prefix_union = fields.Char('Prefix NSFP', compute='_compute_prefix_union', store=True)

    @api.depends('is_union')
    def _compute_prefix_union(self):
        for record in self:
            record.prefix_union = ''
            if record.is_union:
                record.prefix_union = '070'

    @api.depends('invoice_date')
    def _compute_tax_period(self):
        for record in self:
            if record.invoice_date:
                month = record.invoice_date.month
                if month:
                    record.tax_period = str(month)

    @api.depends('invoice_date')
    def _compute_tax_year(self):
        for record in self:
            if record.invoice_date:
                year = record.invoice_date.year
                if year:
                    record.tax_period = str(year)

    def action_invoice_open(self):
        res = super(AccountMove, self).action_invoice_open()
        if self:
            self.is_efaktur_exported=False
        return res