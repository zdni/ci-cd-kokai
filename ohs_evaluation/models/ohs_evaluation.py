from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class OHSEvaluation(models.Model):
    _name = 'ohs.evaluation'
    _inherit = 'survey.survey'

    user_ids = fields.Many2many('res.users', string='Inspection Officer')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Position', compute='_change_employee_id', store=True)
    date = fields.Datetime('Date', default=fields.Datetime.now())
    code = fields.Char('Form Number', default='New')
    template_id = fields.Many2one('survey.survey', string='Evaluation Template', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('process', 'Process'),
        ('correction', 'Correction'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='State', default='new', required=True, readonly=True)
    nonconformity_ids = fields.One2many('nonconformity.report', 'evaluation_id', string='Nonconformity')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val['name'] == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('contract.issue')
        return super(OHSEvaluation, self).create(vals)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        _logger.warning('_onchange_template_id')
        if self.template_id:
            self.title = self.template_id.title
        _logger.warning(self.title)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            template = self.env['survey.survey'].search([ ('id', '=', val['template_id']) ], limit=1)
            if template:
                val['title'] = template.title
            else:
                raise ValidationError("Title in Template can't be reach! Please check Template again")
        return super(OHSEvaluation, self).create(vals)

    @api.depends('employee_id')
    def _change_employee_id(self):
        for record in self:
            record.job_id = record.employee_id.job_id
            record.department_id = record.employee_id.department_id