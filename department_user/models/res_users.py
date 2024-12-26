from odoo import _, api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    department_id = fields.Many2one('hr.department', string='Department')

    def action_create_employee(self):
        self.ensure_one()
        super(ResUsers, self).action_create_employee()
        
        employee = self.env['hr.employee'].search([ ('user_id', '=', self.id), ('active', '=', True) ], limit=1)
        if employee:
            employee.sudo().write({ 'department_id': self.department_id.id })


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    user_ids = fields.One2many('res.users', 'department_id', string='Users')

    def action_show_users(self):
        self.ensure_one()
        if len(self.user_ids) == 0:
            return

        action = self.env.ref('base.action_res_users').sudo().read()[0]
        action['domain'] = [('id', 'in', self.user_ids.ids)]
        return action