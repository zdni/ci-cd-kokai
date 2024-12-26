from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HardnessTesting(models.Model):
    _name = 'hardness.testing'
    _description = 'Hardness Testing'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', default='New', tracking=True)
    date = fields.Date('Date', tracking=True, default=fields.Date.today())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need Improvement'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', tracking=True)
    location_id = fields.Many2one('hr.work.location', string='Location', tracking=True)
    picking_id = fields.Many2one('stock.picking', string='Picking', tracking=True)
    type = fields.Selection([
        ('hrc', 'Rockwell (HRC)'),
        ('hrb', 'Rockwell (HRB)'),
        ('hb', 'Brinell (HB)'),
        ('hv', 'Vickers (HV)'),
        ('shore', 'Shore'),
    ], string='Measuring Unit', required=True, tracking=True, default='hrc')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default= lambda self: self.env.company.id)

    line_ids = fields.One2many('hardness.line', 'testing_id', string='Line')

    witness_id = fields.Many2one('res.partner', string='Witnessed By')
    note = fields.Text('Notes')

    approval_ids = fields.One2many('approval.request', 'hardness_testing_id', string='Approval')
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count')
    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for record in self:
            record.approval_count = len(record.approval_ids)

    def action_show_approval(self):
        self.ensure_one()
        if self.approval_count == 0:
            return
        action = (self.env.ref('approvals.approval_request_action_all').sudo().read()[0])
        action['domain'] = [('id', 'in', self.approval_ids.ids)]
        return action

    def generate_approval_request(self):
        self.ensure_one()
        category_pr = self.env.ref('hardness_testing.approval_category_data_hardness_testing')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'hardness_testing_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.user_id.name} \n Inspection for DO {self.picking_id.name}"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'requested'
        })
        request = self.approval_ids[self.approval_count-1]
        request.action_confirm()

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('hardness.testing')
        return super().create(vals)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_process(self):
        self.ensure_one()
        self.write({ 'state': 'process' })

    def action_requested(self):
        self.ensure_one()
        self.write({ 'state': 'requested' })

    def action_approved(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Hardness Testing',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Hardness Testing {self.name} yang diajukan disetujui. Silahkan lanjutkan ke proses berikutnya. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'approval.inspection',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_need_improvement(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Hardness Testing',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Hardness Testing {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'approval.inspection',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'need_improvement' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })
        


class HardnessLine(models.Model):
    _name = 'hardness.line'
    _description = 'Hardness Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    testing_id = fields.Many2one('hardness.testing', string='Testing')
    product_id = fields.Many2one('product.product', string='Product')
    move_id = fields.Many2one('stock.move', string='Move')
    min = fields.Float('Requirements (Min)')
    max = fields.Float('Requirements (Max)')
    first_result = fields.Float('First Result')
    second_result = fields.Float('Second Result')
    third_result = fields.Float('Third Result')
    average = fields.Float('Average', compute='_compute_result')
    decision = fields.Selection([
        ('ok', 'OK'),
        ('bad', 'BAD'),
    ], string='Decision', compute='_compute_result')
    date = fields.Date('Date', related='testing_id.date')

    @api.depends('first_result', 'second_result', 'third_result')
    def _compute_result(self):
        for record in self:
            decision = 'bad'
            average = (record.first_result+record.second_result+record.third_result)/3
            if average > record.min and average < record.max:
                decision = 'ok'

            record.average = average
            record.decision = decision