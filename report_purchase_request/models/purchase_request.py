from odoo import _, api, fields, models, http
from odoo.exceptions import ValidationError

import base64
import requests
import logging
_logger = logging.getLogger(__name__)

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    barcode = fields.Binary('Barcode', compute='compute_barcode', store=True)

    def action_print_pdf(self):
        _logger.warning('action_print_pdf')
        if self:
            line_ids = []
            approvers = []

            request = self.env['approval.request'].search([
                ('purchase_request_id.id', '=', self.id),
                ('request_status', '=', 'approved'),
            ], order='id DESC', limit=1)

            for approver in request.approver_ids:
                if approver.status == 'approved':
                    approvers.append({
                        'position': approver.position_id.name,
                        'name': approver.user_id.name,
                        'id': approver.id,
                        'url': f"/api/qrcode?text={http.request.env['ir.config_parameter'].get_param('web.base.url')}/approval?proof={str(approver.id)}"
                    })
            
            number = 1
            for line in self.line_ids:
                line_ids.append({
                    'number': number,
                    'product': line.product_id.display_name,
                    'description': line.name,
                    'qty': line.product_qty,
                    'uom': line.product_uom_id.name,
                })
                number += 1
            data = {
                'name': self.name,
                'department': self.department_id.name,
                'requested_by': self.requested_by.name,
                'qrcode_requested_by': f"/api/qrcode?text={http.request.env['ir.config_parameter'].get_param('web.base.url')}/approval?proof={str(request.id)}",
                'priority': self.priority_id.name,
                'date': self.date_start,
                'due_date': self.due_date,
                'type': 'Project',
                'line_ids': line_ids,
                'description': self.description,
                'approvers': approvers
            }
            return self.env.ref('report_purchase_request.action_report_purchase_request').report_action(self, data=data)
        else:
            raise ValidationError('There is no Purchase Request to print')

    def compute_barcode(self):
        for record in self:
            barcode = self.get_barcode()
            record.write({ 'barcode': barcode })

    def action_print_py3o(self):
        self.compute_barcode()
        _logger.warning("report_purchase_request.action_report_purchase_request_py3o")
        return self.env.ref("report_purchase_request.action_report_purchase_request_py3o").report_action(self, config=False)

    def _get_director(self):
        self.ensure_one()
        director = self.env.company.director_id.name
        return director

    def _get_string_priority(self):
        self.ensure_one()
        priority = dict(self._fields['priority'].selection).get(self.priority)
        return priority

    def _get_string_type(self):
        self.ensure_one()
        type = dict(self._fields['type'].selection).get(self.type)
        return type

    def get_barcode(self):
        data = ""
        try:
            data = base64.b64encode(requests.get('https://odoo.valve.id/api/qrcode?text=zidni').content).replace(b"\n", b"")
            # data = base64.b64encode(requests.get('https://quickchart.io/qr?text=Hello%20world&size=200').content).replace(b"\n", b"")
            _logger.warning(data)
        except Exception as e:
            _logger.warning("Can't load the image from URL")
            logging.exception(e)
        return data