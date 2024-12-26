from odoo import _, api, fields, models

class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    job_id = fields.Many2one('hr.job', string='Job Position')