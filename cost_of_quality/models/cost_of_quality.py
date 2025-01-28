from odoo import _, api, fields, models


class CostQuality(models.Model):
    _name = 'cost.quality'
    _description = 'Cost Quality'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)

    name = fields.Char('Name')
    date = fields.Date('Date', default=fields.Date.today())
    source = fields.Selection([
        ('certification_body', 'Certification Body'),
        ('supplier', 'Supplier'),
        ('governance', 'Governance'),
        ('customer', 'Customer'),
        ('internal', 'Internal Kokai'),
    ], string='Source', required=True, default='certification_body')
    group = fields.Selection([
        ('good', 'Good'),
        ('poor', 'Poor'),
    ], string='Group', default='good', required=True)
    category = fields.Selection([
        ('internal', 'Internal Failure Cost'),
        ('external', 'External Failure Cost'),
        ('appraisal', 'Appraisal Cost'),
        ('prevention', 'Prevention Cost'),
    ], string='Category', default='internal', required=True)
    contract_no = fields.Char('Contract No')
    order_no = fields.Char('Purchase Order No')
    invoice_no = fields.Char('Invoice No')
    description = fields.Text('Description')
    total_usd = fields.Float('Total USD')
    total_idr = fields.Float('Total IDR')
    remarks = fields.Text('Remarks')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('cost.quality')
        return super(CostQuality, self).create(vals)