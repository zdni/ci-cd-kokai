from odoo import _, api, fields, models


class MachineType(models.Model):
    _name = 'machine.type'
    _description = 'Machine Type'

    name = fields.Char('Name', required=True)


class MachineTag(models.Model):
    _name = 'machine.tag'
    _description = 'Machine Tag'

    name = fields.Char('Tag Name', required=True)


class MachineModel(models.Model):
    _name = 'machine.model'
    _description = 'Machine Model'

    name = fields.Char('Name', required=True)
    type_id = fields.Many2one('machine.type', string='Type')
    machine_ids = fields.One2many('machine.tool', 'model_id', string='Machine')
    machine_count = fields.Integer('Machine', compute='_compute_machine_count')
    @api.depends('machine_ids')
    def _compute_machine_count(self):
        for record in self:
            record.machine_count = len(record.machine_ids)


class MachineTool(models.Model):
    _name = 'machine.tool'
    _description = 'Machine Tool'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    name = fields.Char('Name')
    model_id = fields.Many2one('machine.model', string='Model')
    tag_ids = fields.Many2many('machine.tag', string='Tags')
    location_id = fields.Many2one('hr.work.location', string='Location', tracking=True)
    note = fields.Text('Note')
    # detail machine