from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    state = fields.Selection([
        ('parking', 'Parking'),
        ('usage', 'In Use'),
    ], string='Status', default='parking')

    usage_ids = fields.One2many('fleet.usage', 'fleet_id', string='Usage')
    usage_count = fields.Integer('Usage Count', compute='_compute_usage_count')
    @api.depends('usage_ids')
    def _compute_usage_count(self):
        for record in self:
            record.usage_count = len(record.usage_ids)
    
    def action_show_fleet_usage(self):
        self.ensure_one()
        if self.usage_count == 0:
            return
        action = self.env.ref('fleet_usage.fleet_usage_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.usage_ids.ids)]
        return action


class FleetUsage(models.Model):
    _name = 'fleet.usage'
    _description = 'Fleet Usage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', default='New Request')
    date = fields.Date('Date', default=fields.Date.today(), required=True, tracking=True)
    fleet_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, tracking=True)
    destination = fields.Char('Destination')
    usage_time = fields.Datetime('Usage Time')
    start_odometer = fields.Float('Start Odometer')
    start_tank = fields.Float('Start Tank')
    end_time = fields.Date('End Time')
    end_odometer = fields.Float('End Odometer')
    end_tank = fields.Float('End Tank')
    description = fields.Text('Description')
    driver_id = fields.Many2one('res.users', string='Driver', default=lambda self: self.env.user.id)
    passenger_ids = fields.Many2many('res.users', string='Passenger')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='State', required=True, default='draft')

    equipment_ids = fields.One2many('fleet.equipment.usage', 'usage_id', string='Equipment')
    condition_ids = fields.One2many('fleet.condition.usage', 'usage_id', string='Condition')
    
    approval_ids = fields.One2many(comodel_name='approval.request', inverse_name='fleet_usage_id', string='Approval Request', readonly=True, copy=False, tracking=True)
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count', readonly=True)
    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(rec.mapped('approval_ids'))

    def action_view_approval_request(self):
        self.ensure_one()
        if self.approval_count == 0:
            return
        action = (self.env.ref('approvals.approval_request_action_all').sudo().read()[0])
        approvals = self.mapped('approval_ids')
        action['domain'] = [('id', 'in', approvals.ids)]
        return action

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('fleet.usage')
        return super(FleetUsage, self).create(vals)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_requested(self):
        self.ensure_one()
        category_pr = self.env.ref('fleet_usage.approval_category_data_fleet_usage')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'fleet_usage_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for Usage {self.fleet_id.name} for {self.driver_id.name} \n Fleet Usage for {self.description}"
        }
        approval = self.env['approval.request'].create(vals)
        if not approval:
            raise ValidationError("Can't Request Approval. Please Contact Administrator")
        approval.action_confirm()
        self.write({ 'state': 'requested' })

    def action_approved(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Fleet Usage',
            'user_id': self.driver_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.driver_id.name} \n {self.name} yang diajukan disetujui. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'fleet.usage',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_refused(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Fleet Usage',
            'user_id': self.driver_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.driver_id.name} \n {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'fleet.usage',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'refused' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })


class FleetEquipmentUsage(models.Model):
    _name = 'fleet.equipment.usage'
    _description = 'Fleet Equipment Usage'

    usage_id = fields.Many2one('fleet.usage', string='Usage', required=True)
    equipment_id = fields.Many2one('product.product', string='Equipment')
    out_checked_by_id = fields.Many2one('res.users', string='Out Checked By')
    out = fields.Boolean('Out', default=True)
    out_remarks = fields.Char('Out Remarks', default='-')
    come_checked_by_id = fields.Many2one('res.users', string='Come Checked By')
    come = fields.Boolean('Come', default=True)
    come_remarks = fields.Char('Come Remarks', default='-')


class FleetConditionUsage(models.Model):
    _name = 'fleet.condition.usage'
    _description = 'Fleet Condition Usage'

    usage_id = fields.Many2one('fleet.usage', string='Usage', required=True)
    out_checked_by_id = fields.Many2one('res.users', string='Out Checked By')
    come_checked_by_id = fields.Many2one('res.users', string='Come Checked By')
    part = fields.Selection([
        ('right', 'Right'),
        ('front', 'Front'),
        ('left', 'Left'),
        ('back', 'Back'),
    ], string='Part', required=True)
    out_remarks = fields.Char('Out Remarks', default='-')
    come_remarks = fields.Char('Come Remarks', default='-')