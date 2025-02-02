from odoo import _, api, fields, models


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    interview_ids = fields.One2many('minutes.meeting', 'applicant_id', string='Interview')
    interview_count = fields.Integer('Interview Count', compute='_compute_interview_count')
    @api.depends('interview_ids')
    def _compute_interview_count(self):
        for record in self:
            record.interview_count = len(record.interview_ids)

    def action_show_interview(self):
        if self.interview_count == 0:
            return
        action = (self.env.ref('minutes_of_meeting.minutes_meeting_action').sudo().read()[0])
        action['domain'] = [('id', 'in', self.interview_ids.ids)]
        return action

    def action_view_applicant_meeting_wizard(self):
        self.ensure_one()
        ctx = dict(default_applicant_id=self.id, active_ids=self.ids, default_description='Interview with ' + self.partner_name)
        return {
            'name': _('Interview'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'applicant.meeting.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }


class MinutesMeeting(models.Model):
    _inherit = 'minutes.meeting'

    applicant_id = fields.Many2one('hr.applicant', string='Applicant')
    partner = fields.Char('Applicant', related='applicant_id.partner_name')
    applicant_stage = fields.Char('Applicant Stage')