from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def generate_assignment_task(self):
        self.ensure_one()
        assignment = self.env['assignment.task'].sudo().create({
            'department_ids': [self.env.ref('department_detail.hr_management_data_inventory_logistic').id, self.env.ref('department_detail.hr_management_data_qhse').id],
            'user_id': self.env.user.id,
            'employee_type_ids': [self.env.ref('department_detail.hr_contract_type_head_of_department').id, self.env.ref('department_detail.hr_contract_type_senior_staff').id],
            'assigned_to': 'department',
            'subject': f"Pemberitahuan Penerimaan Produk",
            'description': f"Pemberitahuan untuk departemen terkait mengenai penerimaan produk untuk pembelian {self.name} yang direncanakan akan datang pada {self.date_planned}",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'model': 'purchase.order',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        self.generate_assignment_task()
        return res