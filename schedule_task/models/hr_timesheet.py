from odoo import _, api, fields, models

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    schedule_id = fields.Many2one('schedule.task', string='Schedule', required=True)