from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PriceQuery(models.Model):
    _name = 'price.query'
    _description = 'Price Query Form'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'date ASC'

    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='Request By', readonly=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    
    name = fields.Char('Name', default='New', readonly=True)
    lead_id = fields.Many2one('crm.lead', string='Lead', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', related='lead_id.partner_id')
    inquiry_id = fields.Many2one('sale.order', string='Inquiry', required=True)
    department_ids = fields.Many2many('hr.department', string='Department')
    date = fields.Date('Date', default=fields.Date.today())
    due_date = fields.Date('Due Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='State', required=True, readonly=True, default='draft', compute='_compute_state', store=True)
    line_ids = fields.One2many('price.query.line', 'query_id', string='Line')
    note = fields.Text('Note')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority', required=True, default='high')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('price.query')
        return super(PriceQuery, self).create(vals)

    @api.depends('line_ids.state')
    def _compute_state(self):
        for record in self:
            has_process = record.mapped('line_ids').filtered(lambda line: line.state in ['requested', 'draft'])
            if len(has_process) == 0:
                record.action_done()

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_process(self):
        self.ensure_one()
        if len(self.department_ids) == 0:
            raise ValidationError("Select Department First to Process Request Price Query")
        # send notification to manager of department
        assignment = self.env['assignment.task'].sudo().create({
            'department_ids': self.department_ids.ids,
            'user_id': self.env.user.id,
            'employee_type_ids': [self.env.ref('department_detail.hr_contract_type_head_of_department').id, self.env.ref('department_detail.hr_contract_type_senior_staff').id],
            'assigned_to': 'department',
            'subject': f"Notification new Price Query",
            'description': f"Pemberitahuan untuk departemen terkait mengenai permintaan Price Query untuk Inquiry {self.inquiry_id.name} dari {self.inquiry_id.partner_id.name}. Mohon untuk segera diproses!",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'model': 'price.query',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()
        for line in self.line_ids:
            line.action_requested()
        self.write({ 'state': 'process' })

    def action_done(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Price Query',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Price Query {self.name} telah selesai diproses. Silahkan lanjutkan proses berikutnya berdasarkan persetujuan dan catatan yang ditinggalkan untuk masing-masing produk. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'approval.inspection',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'done' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })

    def process_price_query(self):
        self.ensure_one()
        for line in self.line_ids:
            if line.state not in ['approved', 'potential'] or not line.new_request:
                continue
            # check attribute in product template
            variant_value_ids = []
            for variant in line.variant_ids:
                product_tmpl_attr = self.env['product.template.attribute.line'].search([
                    ('product_tmpl_id', '=', line.product_tmpl_id.id),
                    ('attribute_id', '=', variant.attribute_id.id),
                ])
                if not product_tmpl_attr:
                    raise ValidationError(f"Product don't have attribute {variant.attribute_id.name}")
                else:
                    product_tmpl_attr_value = self.env['product.template.attribute.line'].search([
                        ('product_tmpl_id', '=', line.product_tmpl_id.id),
                        ('attribute_id', '=', variant.attribute_id.id),
                        ('value_ids', 'in', variant.value_ids.ids),
                    ])
                    if not product_tmpl_attr_value:
                        product_tmpl_attr.value_ids = [(4, variant.value_ids.ids[0])]
                product_template_variant_value_ids = self.env['product.template.attribute.value'].search([
                    ('attribute_id', '=', variant.attribute_id.id),
                    ('product_attribute_value_id', '=', variant.value_ids.ids[0]),
                    ('product_tmpl_id', '=', line.product_tmpl_id.id),
                    ('attribute_line_id', '=', product_tmpl_attr.id),
                ], limit=1)
                if not product_template_variant_value_ids:
                    product_template_variant_value_ids = self.env['product.template.attribute.value'].create({
                        'attribute_id': variant.attribute_id.id,
                        'product_attribute_value_id': variant.value_ids.ids[0],
                        'product_tmpl_id': line.product_tmpl_id.id,
                        'attribute_line_id': product_tmpl_attr.id,
                    })
                variant_value_ids.append((4, product_template_variant_value_ids.id))
            # generate product.product
            # try:
            product = self.env['product.product'].create({
                'active': True,
                'can_be_expensed': False,
                'is_critical': True,
                'is_product_variant': True,
                'potential_product': line.state == 'potential',
                'purchase_ok': True,
                'name': line.product_tmpl_id.name,
                'sale_ok': True,
                'list_price': 0,
                'lst_price': 0,
                'standard_price': 0,
                'product_template_attribute_value_ids': variant_value_ids,
                'product_tmpl_id': line.product_tmpl_id.id,
                'uom_id': line.uom_id.id,
                'uom_po_id': line.uom_id.id,
                'detailed_type': line.product_tmpl_id.detailed_type,
                'categ_id': line.product_tmpl_id.categ_id.id,
            })
            # add to inquiry
            self.inquiry_id.write({ 'order_line': [(0,0, {
                'product_id': product.id,
                'product_uom_qty': line.qty,
                'product_uom': line.uom_id.id,
                'price_unit': line.price_unit,
                'drawing_id': line.drawing_id.id,
                'specification_ids': [(0,0, {
                    'type_id': specification.type_id.id,
                    'specification_id': specification.specification_id.id,
                }) for specification in line.specification_ids]
            })] })
            # except:
            #     raise ValidationError("Can't create Product Variant")



class PriceQueryLine(models.Model):
    _name = 'price.query.line'
    _description = 'Line Order of Price Query Form'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    query_id = fields.Many2one('price.query', string='Doc Reference', required=True, ondelete='cascade')
    line_id = fields.Many2one('sale.order.line', string='Line', tracking=True)
    product_id = fields.Many2one('product.product', string='Product', tracking=True, related='line_id.product_id')
    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True, tracking=True)
    qty = fields.Float('Qty', default=1.0, required=True, tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UoM', required=True, tracking=True)
    need_price = fields.Boolean('Need Price', default=True, tracking=True)
    price_unit = fields.Float('Price Unit', tracking=True)
    need_sheet = fields.Boolean('Need Drawing Sheet', default=True, tracking=True)
    has_sheet = fields.Boolean('Has Drawing Sheet', compute="_compute_has_sheet")
    drawing_id = fields.Many2one('ir.attachment', string='Drawing', tracking=True)
    variant_ids = fields.One2many('line.variant', 'line_id', string='Attributes & Variant')
    specification_ids = fields.One2many('line.specification', 'line_id', string='Specification')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('potential', 'Potential'),
        ('refused', 'Refused'),
    ], string='State', required=True, readonly=True, default='draft', tracking=True)
    remark = fields.Char('Remark', tracking=True)
    new_request = fields.Boolean('Is New Request?', default=True)

    @api.depends('need_sheet', 'drawing_id')
    def _compute_has_sheet(self):
        for record in self:
            if not record.need_sheet or record.drawing_id:
                record.has_sheet = True

    def action_requested(self):
        self.ensure_one()
        self.write({ 'state': 'requested' })

    def action_approved(self):
        self.ensure_one()
        for variant in self.variant_ids:
            if len(variant.value_ids) > 1:
                raise ValidationError(f"Choose one value of attribute {variant.attribute_id.name} in {self.product_tmpl_id.name}")
        self.write({ 'state': 'approved' })

    def action_potential(self):
        self.ensure_one()
        self.write({ 'state': 'potential' })

    def action_refused(self):
        self.ensure_one()
        self.write({ 'state': 'refused' })

class LineVariant(models.Model):
    _name = 'line.variant'
    _description = 'Variant of Price Query Line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    line_id = fields.Many2one('price.query.line', string='Line Ref', required=True, ondelete='cascade')
    attribute_id = fields.Many2one('product.attribute', string='Attribute', required=True)
    value_ids = fields.Many2many('product.attribute.value', string='Values', domain="[('attribute_id', '=', attribute_id)]")
    product_tmpl_value_ids = fields.Many2many('product.template.attribute.value', string='Values')


class LineSpecification(models.Model):
    _name = 'line.specification'
    _description = 'Specification of Price Query Line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    line_id = fields.Many2one('price.query.line', string='Line Ref', ondelete='cascade')
    type_id = fields.Many2one('manufacturing.type', string='Specification')
    specification_id = fields.Many2one('standard.manufacturing', string='Value', domain="[('type_id', '=', type_id)]")