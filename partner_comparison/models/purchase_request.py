from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    state = fields.Selection(selection_add=[('comparison', 'Vendor Comparison'), ('sent', 'Sent')], string='Status', ondelete={'comparison': 'cascade', 'sent': 'cascade'})
    sent_to_ids = fields.Many2many('res.users', string='Sent Agreement To')
    sent_to_id = fields.Many2one('department.team', string='Sent Agreement To', tracking=True)
    potential_partner_ids = fields.Many2many('res.partner', string='Potential Vendor')
    agreement_ids = fields.One2many('purchase.agreement', 'request_id', string='Agreement')
    agreement_count = fields.Integer('Agreement Count', compute='_compute_agreement_count')
    have_comparison = fields.Boolean('Have Comparison', default=True, tracking=True)
    @api.depends('agreement_ids')
    def _compute_agreement_count(self):
        for record in self:
            record.agreement_count = len(record.agreement_ids)

    def _generate_purchase_order(self):
        try:
            self.ensure_one()
            order_line = self.line_ids.filtered(lambda x: not x.cancelled)
            self.env['purchase.order'].create({
                'company_id': self.company_id.id,
                'partner_id': self.partner_id.id,
                'date_order': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'request_id': self.request_id.id,
                'origin': self.request_id.name,
                'order_line': [(0,0,{
                    'product_id': line.product_id.id,
                    'product_qty': line.qty,
                    'product_uom': line.uom_id.id,
                    'purchase_request_lines': [(4,line.id)]
                }) for line in order_line],
            })
        except:
            raise ValidationError("Can't Generate Purchase Order! Please contact Administrator")

    def generate_order(self):
        self.ensure_one()
        if self.agreement_count == 0 and self.have_comparison:
            return
        if self.have_comparison:
            for agreement in self.agreement_ids:
                agreement.generate_purchase_order()
        else:
            self._generate_purchase_order()
        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        action['domain'] = [('request_id', '=', self.id)]
        self.write({ 'state': 'in_progress' })
        return action

    def action_show_agreement(self):
        self.ensure_one()
        if self.agreement_count == 0:
            return
        
        action = self.env.ref('partner_comparison.purchase_agreement_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.agreement_ids.ids)]
        return action

    def action_sent(self):
        self.ensure_one()
        self.sent_purchase_agreement()
        self.write({ 'state': 'sent' })

    def generate_purchase_agreement(self):
        self.ensure_one()

        for partner in self.potential_partner_ids:
            agreement = {
                'partner_id': partner.id,
                'request_id': self.id,
                'line_ids': [(0,0,{
                    'line_id': line.id,
                    'product_id': line.product_id.id,
                    'qty': line.product_qty,
                    'request_id': self.id,
                    'uom_id': line.product_uom_id.id,
                    'partner_id': partner.id,
                }) for line in self.mapped('line_ids').filtered(lambda line: line.product_qty != line.purchased_qty)]
            }
            self.env['purchase.agreement'].create(agreement)
        self.action_show_agreement()
        self.write({ 'state': 'comparison' })

    def sent_purchase_agreement(self):
        self.ensure_one()
        if self.agreement_count == 0:
            return

        assignment = self.env['assignment.task'].create({
            'user_id': self.env.user.id,
            'assigned_to': 'employee',
            'subject': 'Pemberitahuan mengenai Vendor Comparison',
            'description': f"",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'user_ids': self.sent_to_id.member_ids.ids,
            'model': 'purchase.request',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()

        for agreement in self.agreement_ids:
            agreement.action_sent()

    def action_show_price_comparison(self):
        self.ensure_one()
        if self.agreement_count == 0:
            return

        action = self.env.ref('partner_comparison.agreement_line_action').sudo().read()[0]
        action['domain'] = [('agreement_id', 'in', self.agreement_ids.ids), ('agreement_id.state', '=', 'sent')]
        return action

    def action_notif_for_team(self):
        self.ensure_one()
        if self.agreement_count == 0:
            return

        assignment = self.env['assignment.task'].sudo().create({
            'department_ids': [self.team_id.department_id.id],
            'user_id': self.env.user.id,
            'user_ids': self.team_id.member_ids,
            'assigned_to': 'employee',
            'subject': f"Proses PR to PO",
            'description': f"Dear Team {self.team_id.name} \n Pemilihan Vendor dari Vendor Comparison telah selesai. Silahkan buat RFQ untuk masing-masing Vendor yang terpilih. \n Terima Kasih.",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'model': 'purchase.request',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()
        self.write({ 'state': 'in_progress' })