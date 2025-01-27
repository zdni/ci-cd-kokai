from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_asset = fields.Boolean('Is Asset')


class EquipmentCategory(models.Model):
    _name = 'equipment.category'
    _description = 'Equipment Category'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name', required=True)


class EquipmentAsset(models.Model):
    _name = 'equipment.asset'
    _description = 'Equipment Asset'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    responsible_id = fields.Many2one('res.users', string='Responsible')

    name = fields.Char('Name', required=True)
    category_id = fields.Many2one('equipment.category', string='Category')
    used_by = fields.Selection([
        ('department', 'Department'), 
        ('employee', 'Employee'), 
        ('location', 'Location'), 
        ('other', 'Other'), 
    ], string='Used By', required=True, default='employee', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    work_location_id = fields.Many2one('hr.work.location', string='Work Location', tracking=True)
    detail_used_by = fields.Char('Detail Used By', tracking=True)
    note = fields.Text('Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assign'),
        ('maintenance', 'Maintenance'),
        ('return', 'Return'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('equipment.asset')
        return super(EquipmentAsset, self).create(vals)

    @api.onchange('used_by')
    def _onchange_used_by(self):
        for record in self:
            detail_used_by = ''
            if record.used_by == 'department':
                detail_used_by = record.department_id.name
            elif record.used_by == 'employee':
                detail_used_by = record.employee_id.name
            elif record.used_by == 'location':
                detail_used_by = record.work_location_id.name
            record.detail_used_by = detail_used_by

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_assign(self):
        self.ensure_one()
        self.write({ 'state': 'assign' })

    def action_maintenance(self):
        self.ensure_one()
        self.write({ 'state': 'maintenance' })

    def action_return(self):
        self.ensure_one()
        self.write({ 'state': 'return' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })