from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MinutesMeeting(models.Model):
    _name = 'minutes.meeting'
    _description = 'Minutes of Meeting'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    user_id = fields.Many2one('res.users', string='Applicant', default=lambda self: self.env.user.id)
    leader_id = fields.Many2one('res.users', string='Leader')

    name = fields.Char('Name', default='New')
    videocall_url = fields.Char('Videocall URL')
    location_id = fields.Many2one('hr.work.location', string='Location')
    area_id = fields.Many2one('hr.work.area', string='Area')
    detail_location = fields.Char('Detail Location')
    date_start = fields.Datetime('Date Start', default=fields.Datetime.now())
    date_end = fields.Datetime('Date End')

    subject = fields.Text('Subject')
    
    type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], string='Type', required=True, default='internal')
    media = fields.Selection([
        ('meeting', 'Meeting'),
        ('call', 'Call'),
        ('message', 'Message'),
    ], string='Media', required=True, default='meeting')
    participant_type = fields.Selection([
        ('all', 'All'),
        ('department', 'Department'),
        ('employee', 'Employee'),
    ], string='Participant Type', default='all')
    department_ids = fields.Many2many('hr.department', string='Department')
    employee_type_ids = fields.Many2many('hr.contract.type', string='Employee Type')
    user_ids = fields.Many2many('res.users', string='Participants')
    partner_ids = fields.Many2many('res.partner', string='Partner')

    attendance_ids = fields.One2many('meeting.attendance', 'meeting_id', string='Attendance')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assign'),
        ('progress', 'Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='State', required=True, tracking=True, default='draft')

    attachment_ids = fields.Many2many('ir.attachment', string='Files')

    @api.onchange('area_id')
    def _onchange_area_id(self):
        for record in self:
            record.detail_location = record.area_id.name or ""
    
    def action_attend(self):
        self.ensure_one()
        attendance = self.env['meeting.attendance'].search([
            ('meeting_id', '=', self.id),
            ('user_id', '=', self.env.id),
        ], limit=1)
        if attendance:
            attendance.action_attend()
        self.write({ 'is_attend': True })

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_assign(self):
        self.ensure_one()
        assignment = self.env['assignment.task'].create({
            'subject': 'Notification New Meeting',
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
            'assigned_to': self.participant_type,
            'department_ids': self.department_ids.ids,
            'employee_type_ids': self.employee_type_ids.ids,
            'user_ids': self.user_ids.ids,
            'date': fields.Date.today(),
            'start_date': self.date_start,
            'stop_date': self.date_end,
            'work_loc_id': self.location_id.id,
            'area_id': self.area_id.id,
            'description': self.subject,
            'model': 'minutes.meeting',
            'res_id': self.id,
            'schedule_type_id': self.env.ref('mail.mail_activity_data_meeting').id,
        })
        assignment.action_assign()
        self.write({ 'state': 'assign' })

    def action_progress(self):
        self.ensure_one()
        users = []
        if self.participant_type == 'all':
            users = self.env['res.users'].search([
                ('company_id', '=', self.company_id.id),
                ('active', '=', True),
            ])
        if self.participant_type == 'department':
            users = self.env['res.users'].search([
                ('company_id', '=', self.company_id.id),
                ('department_id', 'in', self.department_ids.ids),
                ('employee_id.employee_type_id', 'in', self.employee_type_ids.ids),
                ('active', '=', True),
            ])
        if self.participant_type == 'employee':
            users = self.env['res.users'].search([
                ('id', 'in', self.user_ids.ids),
                ('active', '=', True),
            ])

        if len(users) == 0:
            raise ValidationError("Can't assign Task because User can't Found! Please contact Administrator")

        for user in users:
            self.env['meeting.attendance'].create({
                'meeting_id': self.id,
                'user_id': user.id,
            })
        
        self.write({ 'state': 'progress' })

    def action_done(self):
        self.ensure_one()
        self.write({ 'state': 'done' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })

    def action_attend(self):
        self.ensure_one()
        attend = self.env['meeting.attendance'].search([
            ('user_id', '=', self.env.user.id),
            ('meeting_id', '=', self.id)
        ], limit=1)
        if attend:
            attend.action_attend()


class MeetingAttendance(models.Model):
    _name = 'meeting.attendance'
    _description = 'Meeting Attendance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    meeting_id = fields.Many2one('minutes.meeting', string='Minutes of Meeting', required=True)
    user_id = fields.Many2one('res.users', string='Participant', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    attend_id = fields.Many2one('attendance.value', string='Attend')
    datetime_attend = fields.Datetime('Datetime Attendance')

    def action_attend(self):
        self.ensure_one()
        self.write({ 'datetime_attend': fields.Datetime.now(), 'attend_id': self.env.ref('employee_attendance.attendance_value_data_attendance').id })

class MeetingNote(models.Model):
    _name = 'meeting.note'
    _description = 'Meeting Note'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    meeting_id = fields.Many2one('minutes.meeting', string='Minutes of Meeting', required=True)
    user_id = fields.Many2one('res.users', string='Participant', required=True)
    subject = fields.Char('Subject')
    note = fields.Text('Note')