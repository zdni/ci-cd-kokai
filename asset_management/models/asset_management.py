from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    detail_used_by = fields.Char('Detail Used By')
    note = fields.Html('Note')