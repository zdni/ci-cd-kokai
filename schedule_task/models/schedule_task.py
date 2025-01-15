from odoo import _, api, fields, models, modules
from odoo.exceptions import UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class ScheduleTask(models.Model):
    _name = 'schedule.task'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'date DESC, id DESC'
    _description = 'Schedule Task for User'
    
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)

    assignment_id = fields.Many2one('assignment.task', string='Assignment', tracking=True)
    name = fields.Char('Name', default='New')
    subject = fields.Char('Subject', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', related='user_id.department_id', tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True, tracking=True)
    assign_by_id = fields.Many2one('res.users', string='Assign By', related='assignment_id.user_id', tracking=True)
    schedule_type_id = fields.Many2one('mail.activity.type', string='Schedule Type', tracking=True)
    description = fields.Text('Description', default='-', tracking=True)
    alarm_id = fields.Many2one('schedule.reminder', string='Reminder', default=lambda self: self.env.ref('schedule_task.schedule_reminder_data_notification_one_hour'), required=True, tracking=True)
    work_loc_id = fields.Many2one('hr.work.location', string='Location', tracking=True)
    area_id = fields.Many2one('hr.work.area', string='Area', domain="[('location_id', '=', work_loc_id)]", tracking=True)
    
    date = fields.Date('Date', default=fields.Date.today(), required=True, tracking=True)
    start_date = fields.Datetime('Start At', default=fields.Datetime.now(), tracking=True)
    stop_date = fields.Datetime('Stop At', tracking=True)
    hour_spent = fields.Float('Hour Spent')
    processing_time = fields.Float('Processing Time', compute='_compute_processing_time', store=True)
    timesheet_count = fields.Integer('Timesheet Count', compute='_compute_timesheet_count', store=True)
    timesheet_ids = fields.One2many('account.analytic.line', 'schedule_id', string='Timesheet')
    reason = fields.Char('Cancel Reason', tracking=True)

    # read state
    is_read = fields.Boolean('Is Read', default=False)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assign'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft', tracking=True)
    type = fields.Selection([
        ('notification', 'Notification'),
        ('task', 'Task'),
    ], string='Type', required=True, default='task')

    model = fields.Char(string="Related Document Model", index=True, default='schedule.task')
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

    _state_func = fields.Boolean('State Func', compute='_compute_state_func')
    def _compute_state_func(self):
        for task in self:
            task._state_func = True
            if self.user_id.id == self.env.user.id:
                task.is_read = True
                if task.type == 'notification' and not task.state == 'done':
                    task.action_done()

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('schedule.task')
        return super(ScheduleTask, self).create(vals)
    
    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for schedule in self:
            schedule.res_name = schedule.res_model and \
                self.env[schedule.res_model].browse(schedule.res_id).display_name

    @api.depends('timesheet_ids')
    def _compute_timesheet_count(self):
        for record in self:
            record.timesheet_count = len(record.timesheet_ids)

    @api.depends('start_date', 'stop_date')
    def _compute_processing_time(self):
        for record in self:
            record.processing_time = 0
            if record.start_date and record.stop_date:
                seconds = (record.stop_date - record.start_date).seconds
                record.processing_time = seconds/3600

    def automatic_start_timesheet(self):
        # check if user have timesheet for this schedule
        timesheet = self.env['account.analytic.line'].search([
            ('user_id', '=', self.env.user.id),
            ('schedule_id', '=', self.id),
            ('running', '=', True),
        ])
        if timesheet:
            raise UserError("You can't start timesheet for this schedule again!")
        
        project = self.env['project.project'].search([], limit=1, order="id ASC")
        if not project:
            raise ValidationError("Can't find Internal Project!")
        
        self.write({
            'timesheet_ids': [(0, 0, {
                'user_id': self.env.user.id, 
                'name': self.subject,
                'schedule_id': self.id,
                'start_date': fields.Datetime.now(),
                'date': fields.Date.today(),
                'account_id': project.analytic_account_id.id,
                # 'processing_time': self.processing_time,
                'running': True,
                'project_id': project.id,
            })],
            'state': 'process',
        })

    def action_end_timesheet(self):
        timesheet = self.env['account.analytic.line'].search([
            ('user_id', '=', self.env.user.id),
            ('schedule_id', '=', self.id),
            ('running', '=', True)
        ])
        if timesheet:
            timesheet.action_end_timer()

    def action_show_timesheet(self):
        action = (self.env.ref('hr_timesheet.act_hr_timesheet_line').sudo().read()[0])
        timesheets = self.mapped('timesheet_ids')
        if len(timesheets) > 1:
            action['domain'] = [('id', '=', timesheets.ids)]
        elif timesheets:
            action['views'] = [(self.env.ref('timesheet_grid.timesheet_view_form').id, 'form')]
            action['res_id'] = timesheets.ids[0]
        else:
            return
        return action

    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    def action_assign(self):
        self.ensure_one()
        self.write({'state': 'assign', 'is_read': False})

    def _compute_assignment_state(self):
        if self.assignment_id.handle_by == 'just_one':
            self.assignment_id.action_done()

    def action_done(self):
        self.ensure_one()
        self.action_end_timesheet()
        self.write({'state': 'done', 'stop_date': fields.Datetime.now()})
        self._compute_assignment_state()

    def action_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})

    def action_cancel_has_finished(self):
        self.ensure_one()
        self.action_end_timesheet()
        self.write({ 'state': 'cancel', 'reason': 'Task has been done by other user' })

    def unlink(self):
        for record in self:
            if not record.state == 'cancel':
                raise ValidationError("Can't delete Schedule Task not in Cancel State")
        return super(ScheduleTask, self).unlink()

    @api.model
    def schedule_task_count(self):
        user_tasks = {}
        unread_notification = self.env['schedule.task'].search([
            ('is_read', '=', False),
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'assign'),
            ('type', '=', 'notification'),
        ])
        user_tasks['unread_notification'] = {
            "id": 1,
            "name": 'Notification',
            "model": 'schedule.task',
            "active_field": True,
            "icon": '/schedule_task/static/description/notification.png',
            "type": "unread_notification",
            "domain": "unread_notification",
            'record_count': len(unread_notification),
        }

        unread_tasks = self.env['schedule.task'].search([
            ('is_read', '=', False),
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'assign'),
            ('type', '=', 'task'),
        ])
        user_tasks['unread_task'] = {
            "id": 2,
            "name": 'Unread Schedule Task',
            "model": 'schedule.task',
            "active_field": True,
            "icon": '/schedule_task/static/description/unread-task.png',
            "type": "unread_task",
            "domain": "unread_task",
            'record_count': len(unread_tasks),
        }

        process_tasks = self.env['schedule.task'].search([
            ('is_read', '=', True),
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'process'),
            ('type', '=', 'task'),
        ])
        user_tasks['process_task'] = {
            "id": 3,
            "name": 'Task in Progress',
            "model": 'schedule.task',
            "active_field": True,
            "icon": '/schedule_task/static/description/process-task.png',
            "type": "process_task",
            "domain": "process_task",
            'record_count': len(process_tasks),
        }

        overdue_tasks = self.env['schedule.task'].search([
            ('is_read', '=', True),
            ('user_id', '=', self.env.user.id),
            ('state', 'in', ['assign', 'process']),
            ('type', '=', 'task'),
            ('date', '>', fields.Date.today().strftime('%Y-%m-%d'))
        ])
        user_tasks['overdue_task'] = {
            "id": 4,
            "name": 'Overdue Task',
            "model": 'schedule.task',
            "active_field": True,
            "icon": '/schedule_task/static/description/overdue-task.png',
            "type": "overdue_task",
            "domain": "overdue_task",
            'record_count': len(overdue_tasks),
        }


        return list(user_tasks.values())

    def _prepare_assignment_task(self):
        return {
            'subject': self.subject,
            'assigned_to': 'employee',
            'department_ids': [self.user_id.department_id.id],
            'schedule_type_id': self.schedule_type_id.id,
            'alarm_id': self.alarm_id.id,
            'work_loc_id': self.work_loc_id.id,
            'area_id': self.area_id.id,
            'description': f"Pengalihan Tugas \n {self.description}",
            'date': self.date,
            'start_date': self.start_date,
            'stop_date': self.stop_date,
            'hour_spent': self.hour_spent,
            'processing_time': self.processing_time,
            'type': self.type,
            'model': self.model,
            'res_id': self.res_id,
            'state': 'draft',
            'parent_id': self.assignment_id.id,
        }

    def generate_assign_to_user(self):
        self.ensure_one()
        val = self._prepare_assignment_task()
        new_task = self.env['assignment.task'].sudo().create(val)
        if not new_task:
            raise ValidationError("Error when assign Task! Please contact Administrator")

        self.action_done()

        action = self.env.ref('schedule_task.assignment_task_action').sudo().read()[0]
        action['views'] = [(self.env.ref('schedule_task.assignment_task_view_form').id, 'form')]
        action['res_id'] = new_task.id
        
        return action

