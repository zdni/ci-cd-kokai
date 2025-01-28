from odoo import _, api, fields, models


class HRContractState(models.Model):
    _name = 'hr.contract.state'
    _description = 'HR Contract State'

    name = fields.Char('Name')
    salary_type = fields.Selection([
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    ], string='Salary Type', default='monthly', required=True)

    def name_get(self):
        res = []
        for state in self:
            name = f"{state.name} ({dict(self._fields['salary_type'].selection).get(state.salary_type)})"
            res.append((state.id, name,))
        return res


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    contract_state_id = fields.Many2one('hr.contract.state', string='Contract State')
    tin = fields.Char('Taxpayer Identification Number (TIN)')


# class ResUsers(models.Model):
#     _inherit = 'res.users'

#     contract_state_id = fields.Many2one('hr.contract.state', string='Contract State', related='employee_id.contract_state_id')
#     tin = fields.Char('Taxpayer Identification Number (TIN)', related='employee_id.tin')