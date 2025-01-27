from odoo import _, api, fields, models


class EmployeeTrackingLocation(models.Model):
    _name = 'employee.tracking.location'
    _description = 'Employee Tracking Location'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='user_id.employee_id')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    name = fields.Char('Name')
    date = fields.Datetime('Date', default=fields.Datetime.now())
    location_id = fields.Many2one('hr.work.location', string='Location')
    area_id = fields.Many2one('hr.work.area', string='Area')
    longitudinal = fields.Char('Longitudinal')
    latitude = fields.Char('Latitude')

    # @api.model_create_multi
    # def create(self, vals):
    #     for val in vals:
    #         val['name'] = self.env['ir.sequence'].next_by_code('employee.tracking.location')
    #     return super(EmployeeTrackingLocation, self).create(vals)