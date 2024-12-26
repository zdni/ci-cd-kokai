from odoo import _, api, fields, models

class DepartmentActivity(models.Model):
    _name = 'department.activity'
    _description = 'Activities of Each Department'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name', required=True)
    parent_id = fields.Many2one('department.activity', string='Parent Activity')
    activity_id = fields.Many2one('mail.activity.type', string='Mail Activity')
    description = fields.Text('Description')
    department_id = fields.Many2one('hr.department', string='Department', default=lambda self: self.env.user.department_id.id)
    processing_time = fields.Float('Processing Time', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)