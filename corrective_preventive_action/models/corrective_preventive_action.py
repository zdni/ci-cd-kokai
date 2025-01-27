from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class CARType(models.Model):
    _name = 'car.type'
    _description = 'CAR Type'

    name = fields.Char('Name')
    alias = fields.Char('Alias')


class CarStandard(models.Model):
    _name = 'car.standard'
    _description = 'CAR Standard'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    car_id = fields.Many2one('car.report', string='CAR')
    standard_id = fields.Many2one('list.of.documents', string='Standard Specification', tracking=True)
    section = fields.Char('Section', tracking=True, compute='_compute_section', store=True)
    name = fields.Char('Clause', tracking=True)
    description = fields.Char('Description')
    @api.depends('name')
    def _compute_section(self):
        for record in self:
            if record.name:
                record.section = record.name[:1]


class RootCauseCar(models.Model):
    _name = 'root.cause.car'
    _description = 'Root Cause CAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id, tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)
    car_id = fields.Many2one('car.report', string='CAR', tracking=True)
    name = fields.Text('Root Cause', tracking=True)


class CorrectionCar(models.Model):
    _name = 'correction.car'
    _description = 'Correction CAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id, tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)
    car_id = fields.Many2one('car.report', string='CAR', tracking=True)
    root_id = fields.Many2one('root.cause.car', string='Root Cause', tracking=True, domain="[('car_id', '=', car_id)]")
    name = fields.Text('Correction Action', tracking=True)
    pic_id = fields.Many2one('res.users', string='PIC', tracking=True)
    due_date = fields.Date('Due Date', tracking=True)
    completion_date = fields.Date('Completion Date', tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('submit', 'Submit'),
        ('need_improvement', 'Need Improvement'),
        ('closed', 'Closed'),
    ], string='State', required=True, default='open', tracking=True)


class CorrectiveCar(models.Model):
    _name = 'corrective.car'
    _description = 'Corrective CAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id, tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)
    car_id = fields.Many2one('car.report', string='CAR', tracking=True)
    root_id = fields.Many2one('root.cause.car', string='Root Cause', tracking=True, domain="[('car_id', '=', car_id)]")
    name = fields.Text('Corrective Action', tracking=True)
    pic_id = fields.Many2one('res.users', string='PIC', tracking=True)
    due_date = fields.Date('Due Date', tracking=True)
    completion_date = fields.Date('Completion Date', tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('submit', 'Submit'),
        ('need_improvement', 'Need Improvement'),
        ('closed', 'Closed'),
    ], string='State', required=True, default='open', tracking=True)


class HistoryStateCar(models.Model):
    _name = 'history.state.car'
    _description = 'History State CAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id, tracking=True)
    car_id = fields.Many2one('car.report', string='CAR', tracking=True)
    name = fields.Char('State', tracking=True)
    old_state = fields.Char('Old State', tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)


class CommentCar(models.Model):
    _name = 'comment.car'
    _description = 'Comment CAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    car_id = fields.Many2one('car.report', string='CAR', tracking=True)
    name = fields.Text('Comment')
    user_id = fields.Many2one('res.users', string='User', tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)


class CARCar(models.Model):
    _name = 'car.report'
    _description = 'CAR Corrective - Preventive Action'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    
    approver_id = fields.Many2one('res.users', string='Approver')
    team_id = fields.Many2one('department.team', string='Team')
    name = fields.Char('Name', tracking=True)
    date = fields.Date('Date', tracking=True)
    work_order_no = fields.Char('Work Order No', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    document_id = fields.Many2one('list.of.documents', string='Controlling Document')
    issued_to_ids = fields.Many2many('res.users', string='Issued To', domain="[('department_id', '=', department_id)]", tracking=True)
    type_id = fields.Many2one('car.type', string='Source of CAR', tracking=True)
    finding_type = fields.Selection([
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('concern', 'Concern'),
        ('ofi', 'OFI'),
        ('critical', 'Critical'),
    ], string='Finding Type', default='major', required=True, tracking=True)
    product_impact = fields.Selection([
        ('direct', 'Direct Impact'),
        ('indirect', 'Indirect Impact'),
        ('no', 'No Impact'),
    ], string='Product Impact', default='direct', required=True, tracking=True)
    standard_ids = fields.One2many('car.standard', 'car_id', string='Standard Specification')
    description = fields.Text('Requirement Description', tracking=True)
    objective_evidence = fields.Html('Objective Evidence', tracking=True)
    description_nc = fields.Html('Description of Non-Conformance', tracking=True)
    root_ids = fields.One2many('root.cause.car', 'car_id', string='Root Cause')
    correction_ids = fields.One2many('correction.car', 'car_id', string='Correction Action')
    corrective_ids = fields.One2many('corrective.car', 'car_id', string='Corrective Action')
    comment_ids = fields.One2many('comment.car', 'car_id', string='Comments (if any) where the CAR was completed')
    action_verify = fields.Text('Action Performed to verify the effectiveness of CAR', tracking=True)
    history_ids = fields.One2many('history.state.car', 'car_id', string='History State')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('submit', 'Submit'),
        ('need_improvement', 'Need Improvement'),
        ('closed', 'Closed'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft', required=True, tracking=True)
    remarks = fields.Text('Remarks', tracking=True)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_open(self):
        self.ensure_one()
        assignment = self.env['assignment.task'].create({
            'user_id': self.env.user.id,
            'assigned_to': 'employee',
            'subject': 'Notification about New Corrective Action Report',
            'description': f"",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'user_ids': self.issued_to_ids.ids,
            'model': 'car.report',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()
        self.write({ 'state': 'open' })

    def action_submit(self):
        self.ensure_one()
        assignment = self.env['assignment.task'].create({
            'user_id': self.env.user.id,
            'assigned_to': 'employee',
            'subject': 'Notification about New Corrective Action Report',
            'description': f"",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'user_ids': self.issued_to_ids.ids,
            'model': 'car.report',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        self.write({ 'state': 'submit' })

    def action_need_improvement(self):
        self.ensure_one()
        assignment = self.env['assignment.task'].create({
            'user_id': self.env.user.id,
            'assigned_to': 'employee',
            'subject': 'Notification about Correction of NC',
            'description': f"",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'user_ids': [self.approver_id.id],
            'model': 'car.report',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        self.write({ 'state': 'need_improvement' })

    def action_closed(self):
        self.ensure_one()
        assignment = self.env['assignment.task'].create({
            'user_id': self.env.user.id,
            'assigned_to': 'employee',
            'subject': 'Notification about Closed of Corrective Action Report',
            'description': f"",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'user_ids': self.issued_to_ids.ids,
            'model': 'car.report',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        self.write({ 'state': 'closed' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            prefix = 'CAR'
            type = self.env['car.type'].search([ ('id', '=', val['type_id']) ], limit=1)
            if type:
                prefix = type.alias
            val['name'] = f"{prefix}/{self.env['ir.sequence'].next_by_code('car.report')}"
        
        res = super(CARCar, self).create(vals)
        for record in res:
            self.env['history.state.car'].create({
                'name': 'Open',
                'car_id': record.id,
                'old_state': 'Draft',
                'date': fields.Date.today(),
                'user_id': self.env.user.id,
            })
        return res

    def write(self, vals):
        if vals.get('state', False):
            try:
                self.env['history.state.car'].create({
                    'name': vals['state'],
                    'car_id': self.id,
                    'old_state': dict(self._fields['state'].selection).get(self.state),
                    'date': fields.Date.today(),
                    'user_id': self.env.user.id,
                })
            except UserError as e:
                raise UserError(str(e))
        return super(CARCar, self).write(vals)