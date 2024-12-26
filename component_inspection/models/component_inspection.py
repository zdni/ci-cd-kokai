from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ApprovalInspection(models.Model):
    _name = 'approval.inspection'
    _description = 'Approval Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date DESC, id DESC'

    name = fields.Char('Name', default='New')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need Improvement'),
        ('cancel', 'Cancel'),
    ], string='Status', required=True, tracking=True)
    inspection_ids = fields.One2many('component.inspection', 'approval_id', string='Inspection')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    approval_ids = fields.One2many('approval.request', 'component_inspection_id', string='Approval')
    date = fields.Datetime('Date', default=fields.Datetime.now(), tracking=True)
    requested_date = fields.Datetime('Requested Date', tracking=True)
    closing_date = fields.Datetime('Closing Date', tracking=True)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft', 'closing_date': False })

    def action_process(self):
        self.ensure_one()
        self.write({ 'state': 'process' })

    def action_requested(self):
        self.ensure_one()
        self.write({ 'state': 'requested', 'requested_date': fields.Datetime.now() })

    def action_approved(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Component Testing',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Component Testing {self.name} yang diajukan disetujui. Silahkan lanjutkan ke proses berikutnya. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'approval.inspection',
            'res_id': self.id,
        })
        notification.action_assign()
        self.picking_id.write({ 'state': 'quality_pass' })

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Component Inspection',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Component Inspection {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'approval.inspection',
            'res_id': self.id,
        })
        notification.action_assign()

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel', 'closing_date': fields.Datetime.now() })

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('approval.inspection')
        return super(ApprovalInspection, self).create(vals)
    
    approval_ids = fields.One2many(comodel_name='approval.request', inverse_name='component_inspection_id', string='Approval Request', readonly=True, copy=False, tracking=True)
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count', readonly=True)
    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(rec.mapped('approval_ids'))

    def generate_approval_request(self):
        self.ensure_one()
        category_pr = self.env.ref('component_inspection.approval_category_data_component_inspection')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'component_inspection_id': self.id,
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

    def action_view_approval_request(self):
        self.ensure_one()
        if self.approval_count == 0:
            return
        action = (self.env.ref('approvals.approval_request_action_all').sudo().read()[0])
        approvals = self.mapped('approval_ids')
        action['domain'] = [('id', 'in', approvals.ids)]
        return action

    def action_show_inspection(self):
        self.ensure_one()
        if len(self.inspection_ids) == 0:
            return
        action = (self.env.ref('component_inspection.component_inspection_action').sudo().read()[0])
        action['domain'] = [('id', 'in', self.inspection_ids.ids)]
        return action



class ComponentInspection(models.Model):
    _name = 'component.inspection'
    _description = 'Component Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date DESC, id DESC'

    approval_id = fields.Many2one('approval.inspection', string='Approval')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    name = fields.Char('Name', default='New', tracking=True)
    move_id = fields.Many2one('stock.move', string='Move', tracking=True)
    product_id = fields.Many2one('product.product', string='Product', related='move_id.product_id')
    category = fields.Selection([
        ('incoming', 'Receiving'),
        ('mrp_operation', 'Process'),
        ('internal', 'Internal Transfer'),
        ('outgoing', 'Outgoing'),
    ], string='Category', required=True, tracking=True)
    date = fields.Datetime('Report Date', default=fields.Datetime.now(), required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Inspector', default=lambda self: self.env.user.id, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, tracking=True)
    note = fields.Text('Note', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('requested', 'Requested Approval'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need Improvement'),
        ('cancel', 'Cancel'),
    ], string='Status', required=True, tracking=True, related='approval_id.state')
    line_ids = fields.One2many('inspection.line', 'inspection_id', string='Line')
    qty = fields.Float('Qty')
    uom_id = fields.Many2one('uom.uom', string='UoM', related='move_id.product_uom')
    edition = fields.Integer('Edition', default=1)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('component.inspection')
        return super(ComponentInspection, self).create(vals)


class InspectionLine(models.Model):
    _name = 'inspection.line'
    _description = 'Inspection Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, tracking=True)
    inspection_id = fields.Many2one('component.inspection', string='Inspection', ondelete='cascade')
    section = fields.Selection([
        ('material', 'Material'),
        ('dimension', 'Dimension'),
        ('appearance', 'Appearance'),
    ], string='Type', required=True)
    item = fields.Char('Item')
    standard = fields.Char('Standard and Tolerance')
    method = fields.Char('Method')
    is_good = fields.Boolean('Is Good', default=True)
    remarks = fields.Text('Remarks')