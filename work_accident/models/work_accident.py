from odoo import _, api, fields, models
import logging


_logger = logging.getLogger(__name__)


class BodyPart(models.Model):
    _name = 'body.part'
    _description = 'Body Part'

    name = fields.Char('Name')


class TypeWound(models.Model):
    _name = 'type.wound'
    _description = 'Type Wound'

    name = fields.Char('Name')


class MedicalTreatment(models.Model):
    _name = 'medical.treatment'
    _description = 'Medical Treatment'

    name = fields.Char('Name')
    description = fields.Text('Description')


class WorkAccident(models.Model):
    _name = 'work.accident'
    _description = 'Work Accident'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    active = fields.Boolean('Active', default=True, tracking=True)

    report_by_id = fields.Many2one('res.users', string='Report By', default=lambda self: self.env.user.id)
    name = fields.Char('Name', default='New', required=True, tracking=True)
    date = fields.Datetime('Accident Date', default=fields.Datetime.now(), tracking=True)
    job_id = fields.Many2one('hr.job', string='Job', required=True, tracking=True)
    detail_job = fields.Char('Detail Job')
    work_location_id = fields.Many2one('hr.work.location', string='Work Location', tracking=True)
    area_id = fields.Many2one('hr.work.area', string='Area', tracking=True)
    detail_location = fields.Char('Detail Location', tracking=True)
    work_equipment = fields.Char('Work Equipment')
    product_id = fields.Many2one('product.product', string='Material')
    description = fields.Text('Description', tracking=True)

    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    body_part_ids = fields.Many2many('body.part', string='Injured Body Part')
    type_wound_ids = fields.Many2many('type.wound', string='Type of Wound')
    treatment_ids = fields.Many2many('medical.treatment', string='Medical Treatment')
    detail_treatment = fields.Text('Detail Treatment')

    approval_ids = fields.One2many('approval.request', 'accident_id', string='Approval')
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_ids')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need Improvement'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft')

    @api.onchange('area_id')
    def _onchange_area_id(self):
        for record in self:
            record.detail_location = record.area_id.name or ""

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('work.accident')
        return super(WorkAccident, self).create(vals)

    @api.depends('approval_ids')
    def _compute_approval_ids(self):
        for record in self:
            record.approval_count = len(record.approval_count)

    def generate_approval_request(self):
        self.ensure_one()
        self.action_request()

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_request(self):
        self.ensure_one()
        self.write({ 'state': 'request' })

    def action_approved(self):
        self.ensure_one()
        self.write({ 'state': 'approved' })

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })