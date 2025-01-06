from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_date = fields.Datetime('Start Time')
    end_date = fields.Datetime('End Time')
    unit_amount = fields.Float('Hours Spent', compute='_compute_hours_spent', store=True)
    running = fields.Boolean('Running', default=False)
    is_end = fields.Boolean('Is End', default=False)
    before_timesheet = fields.Image('Before Timesheet', max_width=100, max_height=100)
    after_timesheet = fields.Image('After Timesheet', max_width=100, max_height=100)
    account_id = fields.Many2one('account.analytic.account', string='Account', default=1, required=True, store=True, copy=True, ondelete='restrict', index=True)

    def action_start_timer(self):
        self.ensure_one()
        self.sudo().write({ 'running': True, 'start_date': fields.Datetime.now() })

    def action_end_timer(self):
        self.ensure_one()
        self.sudo().write({ 'running': False, 'end_date': fields.Datetime.now() })

    @api.depends('start_date', 'end_date')
    def _compute_hours_spent(self):
        for record in self:
            if record.start_date and record.end_date:
                timer = record.end_date - record.start_date
                secs=timer.seconds
                hours_spent = secs/3600

                record.is_end = True
                record.unit_amount = hours_spent

class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    processing_time = fields.Float('Processing Time', default=1)