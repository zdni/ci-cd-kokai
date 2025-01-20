from odoo import _, api, fields, models

import base64
import requests
import logging

_logger = logging.getLogger(__name__)

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    approval_ids = fields.One2many(comodel_name='approval.request', inverse_name='purchase_request_id', string='Approval Request', readonly=True, copy=False, tracking=True)
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count', readonly=True)
    state = fields.Selection(selection_add=[ ('need_improvement', 'Need Improvement') ], ondelete={'need_improvement': 'cascade'})

    qrcode_request_by = fields.Binary('Qrcode Request By', compute='_compute_qrcode_request_by', store=True)
    qrcode_approved_by = fields.Binary('Qrcode Approved By', compute='_compute_qrcode_approved_by', store=True)
    qrcode_director = fields.Binary('Qrcode Director', compute='_compute_qrcode_director', store=True)

    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(rec.mapped('approval_ids'))

    def generate_approval_request(self):
        self.ensure_one()

        category_pr = self.env.ref('approvals_purchase_request.approval_category_data_purchase_request')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'purchase_request_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.requested_by.name} \n {self.description}"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'to_approve'
        })
        
        request = self.approval_ids[self.approval_count-1]
        approver = self.env['approval.approver'].search([
            ('request_id.id', '=', request.id),
            ('user_id.id', '=', 2),
        ])
        if approver:
            approver.sudo().write({ 'user_id': self.approver_id.id })
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
            'subject': 'Notifikasi Approve Purchase Request',
            'user_id': self.requested_by.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.requested_by.name} \n Purchase Request {self.name} yang diajukan telah disetujui. Silahkan lanjutkan proses permintaan kepada Tim Purchasing dengan menekan tombol Action 'In Progress'. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'purchase.request',
            'res_id': self.id,
        })
        notification.action_assign()
        self._compute_qrcode_request_by()
        self._compute_qrcode_approved_by()
        self._compute_qrcode_director()

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Purchase Request',
            'user_id': self.requested_by.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.requested_by.name} \n Purchase Request {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'purchase.request',
            'res_id': self.id,
        })
        notification.action_assign()

    def generate_qrcode(self):
        self.ensure_one()
        _logger.warning('start generate_qrcode')
        self._compute_qrcode_request_by()
        self._compute_qrcode_approved_by()
        self._compute_qrcode_director()
        _logger.warning('done generate_qrcode')

    def _compute_qrcode_request_by(self):
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
            record.write({ 'qrcode_request_by': barcode })

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

    def _compute_qrcode_director(self):
        for record in self:
            barcode = ""
            try:
                approver = record.approval_ids[record.approval_count-1].approver_ids[0]
                link = f"https://odoo.valve.id/approval?proof={approver.id}"
                barcode = base64.b64encode(requests.get(f"https://odoo.valve.id/api/qrcode?text={link}").content).replace(b"\n", b"")
            except Exception as e:
                _logger.warning("Can't load the image from URL")
                logging.exception(e)
            record.write({ 'qrcode_director': barcode })
