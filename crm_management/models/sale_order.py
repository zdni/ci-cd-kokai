from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

CODE_CONTRACT = {
    'tender': 'contract.review.a',
    'retail': 'contract.review.c',
}


class RequirementLine(models.Model):
    _name = 'requirement.line'
    _description = 'Requirement Line for Customer and Project'

    order_id = fields.Many2one('sale.order', string='Order', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    type = fields.Selection([
        ('customer', 'Customer'),
        ('project', 'Project'),
    ], string='Type', required=True, default='project')

    @api.model_create_multi
    def create(self, vals):
        lines = super(RequirementLine, self).create(vals)
        for line in lines:
            msg = f"New Requirement `{line.description}` for {line.department_id.name} has been added."
            line.order_id.message_post(body=msg)
        return lines

    def write(self, vals):
        self._log_requirement_tracking(vals)
        return super(RequirementLine, self).write(vals)

    def unlink(self):
        for line in self:
            msg = f"Requirement `{line.description}` for {line.department_id.name} has been deleted."
            line.order_id.message_post(body=msg)
        return super(RequirementLine, self).unlink()

    def _log_requirement_tracking(self, vals):
        for line in self:
            datum = {}
            if 'description' in vals:
                datum.update({'Description': [line.description, vals.get('description')]})
            if datum:
                line.order_id.message_post_with_view('crm_management.track_requirement_ids', values={'line': line, 'datum': datum})

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _default_manager_id(self):
        return self.team_id.user_id.id or False

    @api.onchange('user_id')
    def _onchange_user_id(self):
        for record in self:
            record.write({ 'manager_id': record.team_id.user_id.id or False })

    attachment_ids = fields.Many2many('ir.attachment', string='Attachment')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    state = fields.Selection(selection_add=[
        ('inquiry', 'Inquiry'), 
        ('issue', 'Issue')
    ], ondelete={
        'inquiry': 'cascade',
        'issue': 'cascade',
    })
    inquiry_number = fields.Char('Inquiry Number', tracking=True)
    contract_number = fields.Char('Contract Number', tracking=True)
    is_frk = fields.Boolean('Is FRK', default=False)
    frk_type = fields.Selection([
        ('a', 'A - Audit'),
        ('c', 'C - Non Audit (Marketplace)'),
    ], string='FRK Type', default='c', required=True, tracking=True)
    scope = fields.Char('Scope', tracking=True)
    account_executive_id = fields.Many2one('res.users', string='Account Executive', default=lambda self: self.env.user.id if self.is_frk else False, tracking=True)
    manager_id = fields.Many2one('res.users', string='Manager', default=_default_manager_id, tracking=True)

    # Customer Sales Info in FRK
    customer_inquiry_number = fields.Char('Customer Inquiry Number', tracking=True)
    customer_po_number = fields.Char('Customer PO Number', tracking=True)
    due_date = fields.Date('Due Date', tracking=True)

    # Form Review for FIR and FRK
    source = fields.Selection([
        ('tender', 'Tender'),
        ('retail', 'Retail'),
    ], string='Source', default='retail')
    inquiry_date = fields.Date('Inquiry Date', tracking=True)
    contract_date = fields.Date('Contract Date', tracking=True)
    inquiry_state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('no_quote', 'No Quote'),
        ('done', 'Done'),
        ('lost', 'Lost'),
    ], string='State', default='draft', required=True, tracking=True)
    revision = fields.Integer('Rev', default='0', tracking=True, compute='_compute_revision', store=True)
    description = fields.Text('Description', placeholder='Add a description', tracking=True)

    # Term and Conditions
    packaging = fields.Char('Packaging', tracking=True)
    goods_delivery_procedure = fields.Char('Goods Delivery Procedure', tracking=True)
    handover_procedure = fields.Char('Handover Procedure', tracking=True)
    after_sales_service = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='After Sales Service', tracking=True)
    legal_and_other_applicable_req = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Legal And Other Applicable Req', tracking=True)
    monogram = fields.Selection([
        ('non_monogram', 'Non Monogram'),
        ('api_monogram', 'API Monogram'),
    ], string='Monogram')
    other_painting = fields.Char('Other Painting', tracking=True)

    # Customer Requirement
    is_same_of_project_req = fields.Boolean('Is Same of Project Requirement', default=True)
    customer_requirement_ids = fields.One2many('requirement.line', 'order_id', string='Customer Requirement', domain="[('type', '=', 'customer')]")

    # Project Requirement
    project_requirement_ids = fields.One2many('requirement.line', 'order_id', string='Project Requirement', domain="[('type', '=', 'project')]")

    # approvals sheet
    contract_approval_ids = fields.One2many('approval.request', 'order_id', string='Contract Approval')

    # issue
    contract_issue_ids = fields.One2many('contract.issue', 'order_id', string='Contract Issue')

    @api.depends('contract_issue_ids')
    def _compute_revision(self):
        for record in self:
            record.revision = len([issue.state != 'cancel' for issue in record.contract_issue_ids])

    @api.model_create_multi
    def create(self, vals):
        records = super(SaleOrder, self).create(vals)
        for record in records:
            if record.state == 'inquiry':
                # record.generate_project_requirements()
                msg = f"A new inquiry, `{record.name}` has been created"
                record.lead_id.message_post(body=msg)
        return records

    has_issue = fields.Boolean('Have Issue?', compute='_compute_has_issue')
    @api.depends('contract_issue_ids.state')
    def _compute_has_issue(self):
        for record in self:
            has_issue = False
            for issue in record.contract_issue_ids:
                if not issue.state == 'approved':
                    has_issue = True
            record.has_issue = has_issue

    def generate_frk(self):
        self.ensure_one()
        code = CODE_CONTRACT[self.source]
        contract_number = self.env['ir.sequence'].sudo().next_by_code(code)
        self.write({
            'name': contract_number,
            'state': 'draft',
            'is_frk': True,
        })
        self.action_confirm()

    def generate_approval_request(self):
        self.ensure_one()
        category_pr = self.env.ref('crm_management.approval_category_data_contract_review')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'order_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.user_id.name} \n"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'requested'
        })
        request = self.approval_ids[self.approval_count-1]
        request.action_confirm()

    def action_view_approval_request(self):
        if len(self.contract_approval_ids) == 0:
            return
        action = (self.env.ref('approvals.approval_request_action_all').sudo().read()[0])
        action['domain'] = [('id', 'in', self.contract_approval_ids.ids)]
        return action

    def action_view_contract_issue(self):
        if len(self.contract_issue_ids) == 0:
            return
        action = (self.env.ref('crm_management.contract_issue_action').sudo().read()[0])
        action['domain'] = [('id', 'in', self.contract_issue_ids.ids)]
        return action

    def submit_contract_issue(self):
        self.ensure_one()
        ctx = dict(default_ref_id=self.id, default_document='contract', active_ids=self.ids)
        return {
            'name': _('Submit Issue'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'submit.issue.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }

    def generate_project_requirements(self):
        self.ensure_one()
        departments = self.env['hr.department'].search([ ('include_in_crm', '=', True) ])
        self.write({
            'project_requirement_ids': [(0, 0, {
                'order_id': self.id,
                'department_id': department.id,
                'description': '-',
                'type': 'project',
            }) for department in departments]
        })

    def action_process(self):
        self.ensure_one()
        self.write({ 'inquiry_state': 'process' })

    def action_done(self):
        self.ensure_one()
        self.write({ 'inquiry_state': 'done' })
        self.lead_id.write({ 'state': 'done' })

    def action_confirm(self):
        self.ensure_one()
        self.write({ 'contract_number': self.name })
        return super(SaleOrder, self).action_confirm()

    def set_as_frk(self):
        self.ensure_one()
        self.write({ 'is_frk': True })

    def action_show_contract(self):
        action = (self.env.ref('crm_management.contract_review_action').sudo().read()[0])
        action['views'] = [(self.env.ref('crm_management.contract_review_view_form').id, 'form')]
        action['res_id'] = self._origin.id
        return action


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    specification_ids = fields.One2many('order.line.specification', 'line_id', string='Specification')
    drawing_id = fields.Many2one('product.drawing', string='Drawing')

    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref("sale.sale_order_line_view_form_readonly")
        return {
            "name": _("Detailed Line"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "sale.order.line",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(self.env.context),
        }

    def assign_drawing(self):
        pass


class OrderLineSpecification(models.Model):
    _name = 'order.line.specification'
    _description = 'Order Line Specification'

    line_id = fields.Many2one('sale.order.line', string='Line Ref', ondelete='cascade')
    type_id = fields.Many2one('manufacturing.type', string='Specification')
    specification_id = fields.Many2one('standard.manufacturing', string='Value', domain="[('type_id', '=', type_id)]")


class ProductSpecification(models.Model):
    _inherit = 'product.specification'

    line_id = fields.Many2one('sale.order.line', string='Line')