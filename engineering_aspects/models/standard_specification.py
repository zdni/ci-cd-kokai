from odoo import _, api, fields, models

class StandardManufacturing(models.Model):
    _name = 'standard.manufacturing'
    _description = 'Standard Manufacturing of Product'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', tracking=True)
    type_id = fields.Many2one('manufacturing.type', string='Type', tracking=True, required=True)
    description = fields.Text('Description', tracking=True)
    file = fields.Binary('File', tracking=True)
    file_id = fields.Many2one('ir.attachment', string='File')
    effective_date = fields.Date('Effective Date', tracking=True)
    due_date = fields.Date('Due Date', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('applicable', 'Applicable'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='state', default='draft', tracking=True)
    edition = fields.Integer('Edition', default=0)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)

    def action_draft(self):
        for record in self:
            record.write({ 'state': 'draft' })

    def action_applicable(self):
        for record in self:
            record.write({ 'state': 'applicable' })

    def action_expired(self):
        for record in self:
            record.write({ 'state': 'expired' })

    def action_cancelled(self):
        for record in self:
            record.write({ 'state': 'cancelled' })


class ManufacturingType(models.Model):
    _name = 'manufacturing.type'
    _description = 'Type of Standard Manufacturing'

    name = fields.Char('Name')


class ManufacturingMethod(models.Model):
    _name = 'manufacturing.method'
    _description = 'Manufacturing Method'

    name = fields.Char('Name')
