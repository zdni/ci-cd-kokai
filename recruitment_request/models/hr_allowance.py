from odoo import _, api, fields, models


class HRAllowanceType(models.Model):
    _name = 'hr.allowance.type'
    _description = 'HR Allowance Type'

    name = fields.Char('Name')
    description = fields.Char('Description')