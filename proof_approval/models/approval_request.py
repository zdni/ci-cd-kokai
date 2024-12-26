from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    doc_number = fields.Char('Doc Number')
    request_date = fields.Datetime('Request Date')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['doc_number'] = val['name']
        return super(ApprovalRequest, self).create(vals)

    def action_confirm(self):
        self.write({ 'request_date': fields.Datetime.now() })
        return super(ApprovalRequest, self).action_confirm()

class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'

    date = fields.Date('Date', compute='generate_date', store=True)

    @api.depends('status')
    def generate_date(self):
        for record in self:
            if record.status in ['refused', 'approved']:
                record.write({ 'date': fields.Date.today() })