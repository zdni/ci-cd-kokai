from odoo import _, api, fields, models


class HRContractState(models.Model):
    _name = 'hr.contract.state'
    _description = 'HR Contract State'

    name = fields.Char('Name')
    salary_type = fields.Selection([
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    ], string='Salary Type', default='monthly', required=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    contract_state_id = fields.Many2one('hr.contract.state', string='Contract State')
    tin = fields.Char('Taxpayer Identification Number (TIN)')


# class ResUsers(models.Model):
#     _inherit = 'res.users'

#     contract_state_id = fields.Many2one('hr.contract.state', string='Contract State', related='employee_id.contract_state_id')
#     tin = fields.Char('Taxpayer Identification Number (TIN)', related='employee_id.tin')