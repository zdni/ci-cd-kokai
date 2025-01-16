from odoo import _, api, fields, models


class HRAllowanceType(models.Model):
    _name = 'hr.allowance.type'
    _description = 'HR Allowance Type'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name')
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
    basic_wage = fields.Float('Basic Wage')
