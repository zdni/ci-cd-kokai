from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)



class AssignmentTask(models.Model):
    _name = 'assignment.task'
    _description = 'Assignment Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date DESC, id DESC'

    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)

    parent_id = fields.Many2one('assignment.task', string='Parent', store=True, index=True)
    child_ids = fields.One2many('assignment.task', 'parent_id', string='Child', store=True)

    handle_by = fields.Selection([
        ('all', 'All'),
        ('just_one', 'Just One'),
    ], string='Handle By', required=True, default='all')
    name = fields.Char('Name', default='New Assignment')
    subject = fields.Char('Subject', tracking=True)
    user_id = fields.Many2one('res.users', string='Assigned By', default=lambda self: self.env.user, required=True)
    assigned_to = fields.Selection([
        ('all', 'All'),
        ('department', 'Department'),
        ('team', 'Team'),
        ('employee', 'Employee'),
    ], string='Assigned To', default='all', required=True)
    department_ids = fields.Many2many('hr.department', string='Department', default=lambda self: [self.env.user.department_id.id], tracking=True)
    team_ids = fields.Many2many('department.team', string='Team')
    employee_type_ids = fields.Many2many('hr.contract.type', string='Employee Type', tracking=True)
    user_ids = fields.Many2many('res.users', string='Assigned to', tracking=True)
    schedule_type_id = fields.Many2one('mail.activity.type', string='Task Type', required=True, tracking=True)
    alarm_id = fields.Many2one('schedule.reminder', string='Reminder', default=lambda self: self.env.ref('schedule_task.schedule_reminder_data_notification_one_hour'), required=True)
    work_loc_id = fields.Many2one('hr.work.location', string='Location', tracking=True)
    area_id = fields.Many2one('hr.work.area', string='Area', domain="[('location_id', '=', work_loc_id)]")
    description = fields.Text('Description', default='-', tracking=True)

    date = fields.Date('Date', default=fields.Date.today(), required=True, tracking=True)
    start_date = fields.Datetime('Start At', default=fields.Datetime.now(), tracking=True)
    stop_date = fields.Datetime('Stop At', tracking=True)
    hour_spent = fields.Float('Hour Spent', tracking=True)
    processing_time = fields.Float('Processing Time/User', compute='_compute_processing_time', store=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assign'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft', tracking=True)
    type = fields.Selection([
        ('notification', 'Notification'),
        ('task', 'Task'),
    ], string='Type', required=True, default='task')

    model = fields.Char(string="Related Document Model", index=True, default='assignment.task')
    res_id = fields.Integer(string="Related Document ID", index=True)

    def action_open_document(self):
        try:
            url = f"web#model={self.model}&view_type=form&id={self.res_id}&cids=1"
            return {
                'name': 'Document for Task',
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'current'
            }
        except:
            raise AccessError("URL Document can't be open!")

    @api.onchange('type')
    def _onchange_type(self):
        for record in self:
            if record.type == 'notification':
                record.schedule_type_id = self.env.ref('schedule_task.mail_activity_type_data_notification').id
            else:
                record.schedule_type_id = False

    schedule_ids = fields.One2many('schedule.task', 'assignment_id', string='Schedule')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('assignment.task')
        return super(AssignmentTask, self).create(vals)

    @api.depends('start_date', 'stop_date', 'hour_spent')
    def _compute_processing_time(self):
        for record in self:
            record.processing_time = 0
            if record.start_date and record.stop_date:
                seconds = (record.stop_date - record.start_date).seconds
                record.hour_spent = seconds/3600
                record.processing_time = seconds/3600
            if record.hour_spent:
                record.stop_date = record.start_date + timedelta(hours=record.hour_spent)
                record.processing_time = record.hour_spent

    @api.depends('schedule_ids.state')
    def _compute_state_read(self):
        for record in self:
            _logger.info('_compute_state_read')
            # if document has child
            if len(record.child_ids) > 0:
                child_not_finished = record.mapped('child_ids').filtered(lambda child: child.state in ['assign'])
                if len(child_not_finished) == 0:
                    record.action_done()
                    return

            not_finished = record.mapped('schedule_ids').filtered(lambda schedule: schedule.state in ['assign', 'process'])
            if len(not_finished) == 0:
                record.action_done()

            if record.handle_by == 'just_one':
                has_finished = record.mapped('schedule_ids').filtered(lambda schedule: schedule.state == 'done')
                if len(has_finished) > 0:
                    record.action_done()

    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def _prepare_value_task(self):
        return {
            'company_id': self.company_id.id,
            'assignment_id': self.id,
            'subject': self.subject,
            'assign_by_id': self.user_id.id,
            'schedule_type_id': self.schedule_type_id.id,
            'description': self.description,
            'alarm_id': self.alarm_id.id,
            'work_loc_id': self.work_loc_id.id,
            'start_date': self.start_date,
            'stop_date': self.stop_date,
            'hour_spent': self.hour_spent,
            'state': self.state,
            'type': self.type,
            'model': self.model,
            'res_id': self.id if self.model == self._name else self.res_id,
        }

    def action_assign(self):
        self.ensure_one()
        val = self._prepare_value_task()
        users = []
        if self.assigned_to == 'all':
            users = self.env['res.users'].search([
                ('company_id', '=', self.company_id.id),
                ('active', '=', True),
            ])
        if self.assigned_to == 'department':
            users = self.env['res.users'].search([
                ('company_id', '=', self.company_id.id),
                ('department_id', 'in', self.department_ids.ids),
                ('employee_id.employee_type_id', 'in', self.employee_type_ids.ids),
                ('active', '=', True),
            ])
        if self.assigned_to == 'team':
            for team in self.team_ids:
                user_ids = []
                for member in team.member_ids:
                    user_ids.append(member.id)
                users = self.env['res.users'].search([ ('id', 'in', user_ids) ])
        if self.assigned_to == 'employee':
            users = self.env['res.users'].search([
                ('id', 'in', self.user_ids.ids),
                ('active', '=', True),
            ])

        if len(users) == 0:
            raise ValidationError("Can't assign Task because User can't Found! Please contact Administrator")
        
        for user in users:
            val['user_id'] = user.id
            val['department_id'] = user.department_id.id
            task = self.env['schedule.task'].sudo().create(val)
            task.sudo().action_assign()

        self.write({'state': 'assign'})

    def action_done(self):
        self.ensure_one()
        not_finished = self.mapped('schedule_ids').filtered(lambda schedule: schedule.state in ['assign'])
        for schedule in not_finished:
            schedule.action_cancel_has_finished()
        self.write({'state': 'done'})

    def action_cancel(self):
        self.ensure_one()
        for schedule in self.schedule_ids:
            schedule.action_cancel()
        self.write({'state': 'cancel'})