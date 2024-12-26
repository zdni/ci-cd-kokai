from odoo import _, api, fields, models

class SafetyControl(models.Model):
    _name = 'safety.control'

    inspection_date = fields.Datetime('Inspection Date')
    department_id = fields.Many2one('hr.department', string='Department')
    officer_ids = fields.Many2many('res.users', string='Inspection Officer')
    effective_date = fields.Date('Effective Date')
    code = fields.Char('Form Number', default='New')
    