from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ApplicantMeetingWizard(models.TransientModel):
    _name = 'applicant.meeting.wizard'
    _description = 'Applicant Meeting with Applicant'

    applicant_id = fields.Many2one('hr.applicant', string='Lead', required=True)
    videocall_url = fields.Char('Videocall URL')
    start_date = fields.Datetime('Start At', required=True)
    stop_date = fields.Datetime('Stop At')
    work_loc_id_id = fields.Many2one('hr.work.location', string='Location')
    area_id = fields.Many2one('hr.work.area', string='Area')
    detail_location = fields.Char('Detail Location', tracking=True)
    user_ids = fields.Many2many('res.users', string='Participants', default=lambda self: [self.env.user.id])
    partner = fields.Char('Applicant', related='applicant_id.partner_name')
    description = fields.Text('Description')
    media = fields.Selection([
        ('meeting', 'Meeting'),
        ('call', 'Call'),
        ('message', 'Message'),
    ], string='Media', required=True, default='meeting')
    type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], string='Type', required=True, default='external')

    def action_schedule(self):
        self.ensure_one()
        if not self.applicant_id:
            raise ValidationError("Applicant Interview Failed!")
        
        try:
            meeting = self.env['minutes.meeting'].create({
                'user_id': self.env.user.id,
                'name': 'Interview with ' + self.applicant_id.partner_name,
                'videocall_url': self.videocall_url,
                'location_id': self.work_loc_id_id.id,
                'area_id': self.area_id.id,
                'date_start': self.start_date,
                'date_end': self.stop_date,
                'subject': self.description,
                'type': self.type,
                'media': self.media,
                'partner': self.partner,
                'user_ids': self.user_ids.ids,
                'participant_type': 'employee',
                'applicant_id': self.applicant_id.id,
                'applicant_stage': self.applicant_id.stage_id.name,
            })
            meeting.action_assign()
            action = (self.env.ref('minutes_of_meeting.minutes_meeting_action').sudo().read()[0])
            action['domain'] = [('applicant_id', 'in', [self.applicant_id.id])]
            return action
        except:
            raise ValidationError("Applicant Interview Failed!")