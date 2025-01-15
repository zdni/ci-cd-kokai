from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)


class ScheduleTask(models.Model):
    _inherit = 'schedule.task'

    def automatic_start_timesheet(self):
        res = super(ScheduleTask, self).automatic_start_timesheet()
        # request_product = self.env[self.model].browse(self.res_id)
        # if request_product:
        #     request_product.action_process()
        return res


class RequestProduct(models.Model):
    _name = 'request.product'
    _description = 'Request Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    name = fields.Char('Name', default='New')
    request_date = fields.Datetime('Request Date', default=fields.Datetime.now(), tracking=True)
    closing_date = fields.Datetime('Closing Date', tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    department_id = fields.Many2one('hr.department', string='Department', related='user_id.department_id')
    notes = fields.Text('Notes', tracking=True, default='Request New Product')
    line_ids = fields.One2many('request.product.line', 'request_id', string='Line')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', tracking=True)
    handle_by_id = fields.Many2one('res.users', string='Handle By', tracking=True)
    reply = fields.Text('Reply Message', tracking=True)

    is_group_all_request = fields.Boolean('Is Group All Request', compute='_compute_is_group_all_request')
    def _compute_is_group_all_request(self):
        for record in self:
            is_group_all_request = self.env['res.groups'].search([
                ('id', '=', self.env.ref('request_product.group_request_product_all_request').id),
                ('users', 'in', [self.env.user.id]),
            ])
            record.is_group_all_request = len(is_group_all_request) > 0

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('request.product')
        return super(RequestProduct, self).create(vals)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_requested(self):
        self.ensure_one()

        assignment = self.env['assignment.task'].sudo().create({
            'department_ids': [self.env.ref('department_detail.hr_management_data_inventory_logistic').id],
            'user_id': self.env.user.id,
            'employee_type_ids': [self.env.ref('department_detail.hr_contract_type_head_of_department').id, self.env.ref('department_detail.hr_contract_type_senior_staff').id],
            'assigned_to': 'department',
            'subject': f"Pemberitahuan Permintaan Pembuatan Produk",
            'description': f"Pemberitahuan untuk departemen terkait, berikut pengajuan untuk produk baru yang belum tersedia di dalam sistem. Mohon untuk segera di proses.",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'model': 'request.product',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()

        self.write({ 'state': 'requested', 'request_date': fields.Datetime.now() })

    def action_process(self):
        self.ensure_one()
        self.write({ 'state': 'process' })

    def action_done(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Pembuatan Produk',
            'user_id': self.user_id.id,
            'assign_by_id': self.env.user.id,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Produk yang diajukan telah selesai dibuat. Silahkan cek pesan balasan untuk masing-masing produk yang diajukan untuk mengetahui detail lebih lanjut. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'request.product',
            'res_id': self.id,
        })
        notification.action_assign()
        task = self.env['schedule.task'].search([
            ('user_id', '=', self.env.user.id),
            ('res_id', '=', self.id),
            ('model', '=', 'request.product'),
            ('state', 'in', ['process']),
            ('active', '=', True),
        ], limit=1)
        if task:
            task.action_done()

        self.write({ 'state': 'done', 'closing_date': fields.Datetime.now() })

    def action_cancel(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Pembuatan Produk',
            'user_id': self.user_id.id,
            'assign_by_id': self.env.user.id,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Produk yang diajukan ditolak. Silahkan cek pesan balasan untuk masing-masing produk yang diajukan untuk mengetahui detail lebih lanjut. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'request.product',
            'res_id': self.id,
        })
        notification.action_assign()

        self.write({ 'state': 'cancel', 'closing_date': fields.Datetime.now() })


class RequestProductLine(models.Model):
    _name = 'request.product.line'
    _description = 'Request Product Line'

    product_id = fields.Many2one('product.template', string='Product')
    request_id = fields.Many2one('request.product', string='Request')
    product = fields.Char('Product')
    description = fields.Char('Description')
    img_product = fields.Image('Image Product', max_width=100, max_height=100)
    reason = fields.Char('Reason')
    link = fields.Char('Reference')
    reply = fields.Char('Reply Message')