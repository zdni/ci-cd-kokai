from odoo import _, api, fields, models

class ScheduleReminder(models.Model):
    _name = 'schedule.reminder'
    _description = 'Reminder for User about Own Schedule'

    name = fields.Char('Name', default='New', compute='_compute_name', store=True)
    active = fields.Boolean('Active', default=True)
    type = fields.Selection([
        ('notification', 'Notification'),
        ('email', 'Email'),
    ], string='Type', required=True)
    duration = fields.Integer('Remind Before', default=1)
    interval = fields.Selection([
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
    ], string='Unit', required=True)

    def _generate_name(self):
        return f"{dict(self._fields['type'].selection).get(self.type)} - {str(self.duration)} {dict(self._fields['interval'].selection).get(self.interval)}"

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self._generate_name()
        return super(ScheduleReminder, self).create(vals)

    @api.depends('duration', 'interval')
    def _compute_name(self):
        for record in self:
            record.name = record._generate_name()