from odoo import _, api, fields, models

class DocumentControl(models.Model):
    _name = 'document.control'
    _description = 'Control of List Document'

    active = fields.Boolean('Active', default=True, tracking=True)
    name = fields.Char('Code', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True, tracking=True)
    edition = fields.Integer('Edition/Revision No.', default=0, tracking=True)
    description = fields.Char('Description', required=True, tracking=True)
    issue_date = fields.Date('Issue Date', required=True, tracking=True)
    received_date = fields.Date('Received Date', tracking=True)