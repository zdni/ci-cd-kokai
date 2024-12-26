from odoo import _, api, fields, models

class InspectionList(models.Model):
    _name = 'inspection.list'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    note = fields.Text('Note', default='-')
    parent_id = fields.Many2one('inspection.list', string='Parent')
    child_count = fields.Integer('Child Count', compute='_compute_child_count')
    answer = fields.Selection([
        ('pass', 'Pass'),
        ('nc', 'NC'),
        ('na', 'NA'),
    ], string='Inspection Result', default='na')

    def _compute_child_count(self):
        pass