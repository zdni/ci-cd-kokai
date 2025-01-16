from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)


class EmployeeAttendance(models.Model):
    _name = 'employee.attendance'
    _description = 'Employee Attendance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Name', related='value_id.name')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    date = fields.Datetime('Date', required=True)
    attendance_time = fields.Datetime('Attendance Time', required=True)
    value_id = fields.Many2one('attendance.value', string='Value', required=True)
    description = fields.Char('Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)


class AttendanceValue(models.Model):
    _name = 'attendance.value'
    _description = 'Attendance Value'

    name = fields.Char('Name', required=True)
    value = fields.Integer('Value', required=True)
    color = fields.Char('Color')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    attendance_ids = fields.One2many('employee.attendance', 'employee_id', string='Attendance')

    def action_show_attendance(self):
        self.ensure_one()
        action = self.env.ref('employee_attendance.employee_attendance_action').sudo().read()[0]
        action['domain'] = [('employee_id', '=', self.id)]
        return action


# class ResUsers(models.Model):
#     _inherit = 'res.users'

#     attendance_ids = fields.One2many('employee.attendance', 'user_id', string='Attendance')