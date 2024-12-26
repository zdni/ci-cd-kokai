from odoo import _, api, fields, models


class CertificateOrigin(models.Model):
    _name = 'certificate.origin'
    _description = 'Certificate Origin'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    name = fields.Char('Name', default='New', required=True)
