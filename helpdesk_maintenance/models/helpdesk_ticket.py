from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    def _default_stage_id(self):
        first_stage = self.env['helpdesk.stage'].search([], order='sequence ASC', limit=1)
        if first_stage:
            return first_stage.id
        return False

    active = fields.Boolean('Active', default=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    user_id = fields.Many2one('res.users', string='Customer', default=lambda self: self.env.user.id)
    department_user_id = fields.Many2one('hr.department', string='Department User', related='user_id.department_id')
    
    name = fields.Char('Name', default='New')
    subject = fields.Char('Subject', tracking=True)
    date = fields.Datetime('Date', tracking=True, default=fields.Datetime.now())
    process_date = fields.Datetime('Process Date', tracking=True, compute='_compute_date', store=True)
    solve_date = fields.Datetime('Solve Date', tracking=True, compute='_compute_date', store=True)
    team_id = fields.Many2one('department.team', string='Team', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', related='team_id.department_id')
    description = fields.Text('Description')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very', 'Very High'),
    ], string='Priority', default='low', tracking=True)
    
    tag_ids = fields.Many2many('helpdesk.tag', string='Tags', tracking=True)
    type_id = fields.Many2one('helpdesk.type', string='Type', tracking=True)
    stage_id = fields.Many2one('helpdesk.stage', string='Stage', index=True, tracking=True, default=_default_stage_id, copy=False, group_expand='_read_group_stage_ids', ondelete='restrict')

    response_ids = fields.One2many('helpdesk.activity', 'ticket_id', string='Responses')
    response_count = fields.Integer('Response Count', compute='_compute_response_count')
    @api.depends('response_ids')
    def _compute_response_count(self):
        for record in self:
            record.response_count = len(record.response_ids)
        
    def action_show_response(self):
        self.ensure_one()
        if self.response_count == 0:
            return
        action = self.env.ref('helpdesk_maintenance.helpdesk_activity_action').read()[0]
        action['domain'] = [('id', 'in', self.response_ids.ids)]
        return action

    last_activity_id = fields.Many2one('mail.activity.type', string='Last Activity', compifute='_compute_last_activity', store=True)
    @api.depends('response_ids')
    def last_activity_id(self):
        for record in self:
            activities = record.mapped('response_ids').filtered(lambda activity: activity.state != 'draft')
            if not activities:
                record.last_activity_id = False
            last_activity = activities[len(activities)-1]
            record.last_activity_id = last_activity.activity_id.id

    def assign_notification_to_user(self):
        self.ensure_one()
        user_ids = self.team_id.member_ids.ids
        user_ids.append(self.team_id.user_id.user_id.id)
        assignment = self.env['assignment.task'].sudo().create({
            'assigned_to': 'employee',
            'user_ids': [user_ids],
            'user_id': self.env.user.id,
            'subject': f"Pemberitahuan Permintaan Maintenance",
            'description': f"Pemberitahuan untuk team terkait mengenai permintaan maintenance {self.name} oleh {self.user_id.name} \n f{self.description}",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'model': 'helpdesk.ticket',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket')
        records = super(HelpdeskTicket, self).create(vals)
        for record in self:
            record.assign_notification_to_user()
        return records

    @api.depends('stage_id')
    def _compute_date(self):
        for record in self:
            if record.stage_id.is_progress:
                record.process_date = fields.Datetime.now()
            if record.stage_id.is_close:
                record.solve_date = fields.Datetime.now()

        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Tahap Maintenance',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Maintenance {self.name} yang diajukan sedang dalam tahap {self.stage_id.name}. Untuk detail aktifitas terupdate dapat dilihat pada dokumen {self.name}. \n Terima Kasih.",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'helpdesk.ticket',
            'res_id': self.id,
        })
        notification.action_assign()

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


class HelpdeskActivity(models.Model):
    _name = 'helpdesk.activity'
    _description = 'Helpdesk Activity'
    _order = 'date ASC'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    active = fields.Boolean('Active', default=True, tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    subject = fields.Char('Subject', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True)
    activity_id = fields.Many2one('mail.activity.type', string='Activity', tracking=True)
    name = fields.Char('Name', tracking=True)
    date = fields.Datetime('Date', tracking=True, default=fields.Datetime.now())
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment')
    note = fields.Text('Note')
    state = fields.Selection([
        ('new', 'New'),
        ('cancel', 'Cancel'),
    ], string='Status', default='new', tracking=True)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('helpdesk.activity')
        return super(HelpdeskActivity, self).create(vals)
    
    @api.onchange('subject')
    def _onchange_subject(self):
        for record in self:
            record.note = record.subject