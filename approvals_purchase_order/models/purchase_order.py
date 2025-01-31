from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import base64
import requests
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('approved', 'Approved'), ('need_improvement', 'Need Improvement')], string='Status')
    approval_ids = fields.One2many(comodel_name='approval.request', inverse_name='purchase_order_id', string='Approval Request', readonly=True, copy=False, tracking=True)
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count', readonly=True)

    qrcode_prepared_by = fields.Binary('Qrcode Prepared By', compute='_compute_qrcode_prepared_by', store=True)
    qrcode_approved_by = fields.Binary('Qrcode Approved By', compute='_compute_qrcode_approved_by', store=True)

    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(rec.mapped('approval_ids'))

    def generate_approval_request(self):
        self.ensure_one()
        category_pr = self.env.ref('approvals_purchase_order.approval_category_data_purchase_order')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'purchase_order_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.user_id.name} \n {self.notes}"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'to approve'
        })
        request = self.approval_ids[self.approval_count-1]
        self._compute_qrcode_prepared_by()
        request.action_confirm()

    def action_view_approval_request(self):
        action = (self.env.ref('approvals.approval_request_action_all').sudo().read()[0])
        approvals = self.mapped('approval_ids')
        if len(approvals) > 1:
            action['domain'] = [('id', 'in', approvals.ids)]
        elif approvals:
            action['views'] = [(self.env.ref('approvals.approval_request_view_form').id, 'form')]
            action['res_id'] = approvals.ids[0]
        return action

    def action_approved(self):
        self.ensure_one()
        self.write({ 'state': 'approved' })
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approve Purchase Order',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Purchase Order {self.name} yang diajukan telah disetujui. Silahkan lanjutkan proses Pembelian. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'purchase.order',
            'res_id': self.id,
        })
        notification.action_assign()
        self._compute_qrcode_prepared_by()
        self._compute_qrcode_approved_by()

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Purchase Order',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Purchase Order {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'purchase.order',
            'res_id': self.id,
        })
        notification.action_assign()

    def button_confirm(self):
        if not self.state == 'approved':
            raise ValidationError("Please Request Approval first before confirm PO!")
        self.write({ 'state': 'draft' })
        return super(PurchaseOrder, self).button_confirm()

    def _compute_qrcode_prepared_by(self):
        for record in self:
            barcode = ""
            try:
                approval = record.approval_ids[record.approval_count-1]
                link = f"https://odoo.valve.id/requested?requested={approval.id}"
                barcode = base64.b64encode(requests.get(f"https://odoo.valve.id/api/qrcode?text={link}").content).replace(b"\n", b"")
            except Exception as e:
                _logger.warning("Can't load the image from URL")
                logging.exception(e)
            _logger.warning(barcode)
            record.write({ 'qrcode_prepared_by': barcode })

    def _compute_qrcode_approved_by(self):
        for record in self:
            barcode = ""
            try:
                approver = record.approval_ids[record.approval_count-1].approver_ids[0]
                link = f"https://odoo.valve.id/approval?proof={approver.id}"
                barcode = base64.b64encode(requests.get(f"https://odoo.valve.id/api/qrcode?text={link}").content).replace(b"\n", b"")
            except Exception as e:
                _logger.warning("Can't load the image from URL")
                logging.exception(e)
            record.write({ 'qrcode_approved_by': barcode })
