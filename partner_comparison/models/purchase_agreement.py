from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseAgreement(models.Model):
    _name = 'purchase.agreement'
    _description = 'Purchase Agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {
        'sent': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.depends('line_ids.price_total')
    def _amount_all(self):
        for agreement in self:
            order_lines = agreement.line_ids

            if agreement.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in order_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(agreement.currency_id, {}).get('amount_untaxed', 0.0)
                amount_tax = totals.get(agreement.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(order_lines.mapped('price_subtotal'))
                amount_tax = sum(order_lines.mapped('price_tax'))


            agreement.amount_untaxed = amount_untaxed
            agreement.amount_tax = amount_tax
            amount_total = agreement.amount_untaxed + agreement.amount_tax
            
            discount = 0
            if agreement.has_discount_global:
                if agreement.discount_type == 'percent':
                    discount = amount_total*agreement.discount/100
                if agreement.discount_type == 'fixed':
                    discount = agreement.discount_fixed

            agreement.amount_total = amount_total - discount
            

    @api.depends_context('lang')
    @api.depends('line_ids.tax_ids', 'line_ids.price_subtotal', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.line_ids
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )

    def _default_uom_delivery(self):
        for record in self:
            record.uom_delivery_id = False
            uom = self.env['uom.uom'].search([
                ('category_id', '=', self.env.ref('uom.uom_categ_wtime').id),
                ('uom_type', '=', 'reference'),
            ], limit=1)
            if uom:
                record.uom_delivery_id = uom.id

    def _default_domain(self):
        return [('category_id', '=', self.env.ref('uom.uom_categ_wtime').id)]

    name = fields.Char('Name', default='New Agreement')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    agreement_date = fields.Date('Agreement Date', default=fields.Date.today())
    delivery_time = fields.Float('Delivery Time')
    uom_delivery_id = fields.Many2one('uom.uom', string='UoM', domain=_default_domain)
    request_id = fields.Many2one('purchase.request', string='Purchase Request')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('done', 'Done'),
        ('to_po', 'PO'),
        ('cancel', 'Cancel'),
    ], string='Status', copy=False, default='draft', tracking=True)
    notes = fields.Html('Terms and Conditions')

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=True)
    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    line_ids = fields.One2many('agreement.line', 'agreement_id', string='Line')

    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES, default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    order_id = fields.Many2one('purchase.order', string='Order')

    has_discount_global = fields.Boolean('Has Discount Global')
    discount_type = fields.Selection([
        ('percent', 'Percent'),
        ('fixed', 'Fixed'),
    ], string='Discount Type', default='percent')
    discount = fields.Float(string="Discount (%)", digits="Discount")
    discount_fixed = fields.Float(string="Discount (Fixed)", digits="Discount")

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if not val.get('name'):
                val['name'] = self.env['ir.sequence'].next_by_code('purchase.agreement')
        return super(PurchaseAgreement, self).create(vals)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_sent(self):
        self.ensure_one()
        self.write({ 'state': 'sent' })

    def action_done(self):
        self.ensure_one()
        self.write({ 'state': 'done' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })

    def generate_purchase_order(self):
        try:
            self.ensure_one()
            order_line = self.line_ids.filtered(lambda x: x.is_accept)
            if len(order_line) ==  0:
                return

            self.env['purchase.order'].create({
                'company_id': self.company_id.id,
                'agreement_id': self.id,
                'partner_id': self.partner_id.id,
                'date_order': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'request_id': self.request_id.id,
                'origin': self.request_id.name,
                'order_line': [(0,0,{
                    'agreement_id': line.id,
                    'product_id': line.product_id.id,
                    'product_qty': line.qty,
                    'product_uom': line.uom_id.id,
                    'price_unit': line.price_unit,
                    'taxes_id': line.tax_ids,
                    'discount': line.discount,
                    'discount_fixed': line.discount_fixed,
                    'purchase_request_lines': [(4,line.line_id.id)]
                }) for line in order_line],
            })
            self.action_done()
        except:
            raise ValidationError("Can't Generate Purchase Order! Please contact Administrator")


class AgreementLine(models.Model):
    _name = 'agreement.line'
    _description = 'Agreement Line'

    agreement_id = fields.Many2one('purchase.agreement', string='Agreement')
    request_id = fields.Many2one('purchase.request', string='Purchase Request', related='agreement_id.request_id')
    partner_id = fields.Many2one('res.partner', string='Vendor', related='agreement_id.partner_id', store=True)
    line_id = fields.Many2one('purchase.request.line', string='Line')
    product_id = fields.Many2one('product.product', string='Product', required=True, related='line_id.product_id', store=True)
    qty = fields.Float('Qty', related='line_id.product_qty')
    uom_id = fields.Many2one('uom.uom', string='UoM', related='line_id.product_uom_id')
    price_unit = fields.Float('Price Unit')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Float('Subtotal', compute='_compute_amount')
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    is_accept = fields.Boolean('Accept')
    currency_id = fields.Many2one('res.currency', 'Currency', related='agreement_id.currency_id')
    discount = fields.Float(string="Discount (%)", digits="Discount")
    discount_fixed = fields.Float(string="Discount (Fixed)", digits="Discount")

    @api.depends('product_id', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            amount_total = amount_untaxed + amount_tax

            discount = 0
            if line.discount:
                discount = amount_total*line.discount/100
            if line.discount_fixed:
                discount = line.discount_fixed

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_total-discount,
            })

    def _get_discounted_price_unit(self):
        self.ensure_one()
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        if self.discount_fixed:
            return self.price_unit - self.discount_fixed
        return self.price_unit

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.agreement_id.partner_id,
            currency=self.agreement_id.currency_id,
            product=self.product_id,
            taxes=self.tax_ids,
            price_unit=self._get_discounted_price_unit(),
            quantity=self.qty,
            price_subtotal=self.price_subtotal,
        )