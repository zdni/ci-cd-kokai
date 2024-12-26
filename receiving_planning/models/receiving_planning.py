from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReceivingPlanning(models.Model):
    _name = 'receiving.planning'
    _description = 'Receiving Planning'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', default='New Receiving Planning')
    date_planned = fields.Date('Planning Date', default=fields.Datetime.now())
    order_ids = fields.Many2many('purchase.order', string='Order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assign'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_assign(self):
        self.ensure_one()
        assignment = self.env['assignment.task'].create({
            'department_ids': [self.env.ref('department_detail.hr_management_data_inventory_logistic').id, self.env.ref('department_detail.hr_management_data_qhse').id],
            'user_id': self.env.user.id,
            'employee_type_ids': [self.env.ref('department_detail.hr_contract_type_head_of_department').id, self.env.ref('department_detail.hr_contract_type_senior_staff').id],
            'assigned_to': 'department',
            'subject': f"Pemberitahuan Penerimaan Produk",
            'description': f"Pemberitahuan untuk departemen terkait mengenai penerimaan produk pada {self.date_planned}",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'model': 'receiving.planned',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()
        self.write({ 'state': 'assign' })

    def action_show_delivery_order(self):
        self.ensure_one()
        if len(self.order_ids) == 0:
            return
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('purchase_id', 'in', self.order_ids.ids)]
        return action

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })