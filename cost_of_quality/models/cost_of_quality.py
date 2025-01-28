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
    ], string='Source')
    

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('cost.quality')
        return super(CostQuality, self).create(vals)