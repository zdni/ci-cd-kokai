from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval


class HRAllowanceType(models.Model):
    _name = 'hr.allowance.type'
    _description = 'HR Allowance Type'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name')
    alias = fields.Char('Alias')
    description = fields.Char('Description')
    type = fields.Selection([
        ('main', 'Main'),
        ('addition', 'Addition'),
        ('subtraction', 'Subtraction'),
        ('formula', 'Formula'),
    ], string='Type', default='main')
    wage_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('formula', 'Formula'),
    ], string='Wage Type', default='fixed')
    code = fields.Text('Code',
        default='''
            # Available variables:
            #----------------------
            # employee: hr.employee object
            # contract: hr.contract object
            # allowances: object containing detail allowance in contract, access with type or alias of allowance, or with `sum` for total from type of allowance
            # total_working_days: object containing the computed worked days
            # leave: object containing leave between start and end period.

            # Note: returned value have to be set in the variable 'result'

            result = rules.NET > categories.NET * 0.10''')

    def _compute_rule(self, localdict):
        value = 0
        self.ensure_one()
        is_get = self.env['hr.contract.allowance'].search([
            ('employee_id', '=', localdict['employee'].id),
            ('contract_id', '=', localdict['contract'].id),
            ('allowance_id', '=', self.id),
        ])
        if is_get:
            safe_eval(self.code, localdict, mode="exec", nocopy=True)
        return value