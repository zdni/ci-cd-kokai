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


class AerCategory(models.Model):
    _name = 'aer.category'
    _description = 'Average Effective Rate Category'

    name = fields.Char('Name')
    aer_id = fields.Many2one('average.effective.rate', string='AER')
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced'),
    ], string='Marital', default='single')
    children = fields.Integer('Children')


class AverageEffectiveRate(models.Model):
    _name = 'average.effective.rate'
    _description = 'Average Effective Rate for Income Tax'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name')
    category_ids = fields.One2many('aer.category', 'aer_id', string='Category')
    line_ids = fields.One2many('aer.range', 'aer_id', string='Line')


class AerRange(models.Model):
    _name = 'aer.range'
    _description = 'AER Line'

    aer_id = fields.Many2one('average.effective.rate', string='AER')
    start_range = fields.Float('Start Range')
    end_range = fields.Float('End Range')
    rate = fields.Float('Rate (%)', default=0)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    aer_category_id = fields.Many2one('aer.category', string='AER Category')
    aer_id = fields.Many2one('average.effective.rate', string='AER', related='aer_category_id.aer_id')