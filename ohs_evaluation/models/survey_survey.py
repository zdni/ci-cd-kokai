from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    number = fields.Char('Form Number')
    effective_date = fields.Date('Effective Date')
    revision = fields.Char('Revision')
    state = fields.Selection([
        ('request', 'Request'),
        ('approved', 'Approved'),
        ('not_applicable', 'Not Applicable'),
        ('refused', 'Refused'),
    ], string='State', default='request', required=True, readonly=True)
    # category_id = fields.Many2one('evaluation.category', string='Evaluation Category')