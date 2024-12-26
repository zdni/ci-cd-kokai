from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ScheduleMeetingWizard(models.TransientModel):
    _name = 'schedule.meeting.wizard'
    _description = 'Schedule Meeting with Customer'

    lead_id = fields.Many2one('crm.lead', string='Lead', required=True)
    videocall_url = fields.Char('Videocall URL')
    start_date = fields.Datetime('Start At', required=True)
    stop_date = fields.Datetime('Stop At')
    work_loc_id_id = fields.Many2one('hr.work.location', string='Location')
    area_id = fields.Many2one('hr.work.area', string='Area')
    user_ids = fields.Many2many('res.users', string='Participants', default=lambda self: [self.env.user.id])
    partner_ids = fields.Many2many('res.partner', string='Customer')
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
        if not self.lead_id:
            raise ValidationError("Schedule Meeting Failed!")
        
        try:
            meeting = self.env['minutes.meeting'].create({
                'user_id': self.env.user.id,
                'name': 'Meeting with ' + self.lead_id.partner_id.name,
                'videocall_url': self.videocall_url,
                'location_id': self.work_loc_id_id.id,
                'area_id': self.area_id.id,
                'date_start': self.start_date,
                'date_end': self.stop_date,
                'subject': self.description,
                'type': self.type,
                'media': self.media,
                'user_ids': self.user_ids.ids,
                'participant_type': 'employee',
                'partner_ids': self.partner_ids.ids,
                'lead_id': self.lead_id.id,
                'crm_stage': self.lead_id.stage_id.id,
                'crm_state': self.lead_id.state,
                'lead_id': self.lead_id.id,
            })
            meeting.action_assign()
            action = (self.env.ref('minutes_of_meeting.minutes_meeting_action').sudo().read()[0])
            action['views'] = [(self.env.ref('minutes_of_meeting.minutes_meeting_view_form').id, 'form')]
            action['id'] = meeting.id
            return action
        except:
            raise ValidationError("Schedule Meeting Failed!")