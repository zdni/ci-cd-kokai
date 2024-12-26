from odoo import _, api, fields, models


class TensileTesting(models.Model):
    _name = 'tensile.testing'
    _description = 'Tensile Testing'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', default='New', tracking=True)
    date = fields.Date('Date', tracking=True, default=fields.Date.today())
    picking_id = fields.Many2one('stock.picking', string='Picking', tracking=True)
    move_id = fields.Many2one('stock.move', string='Move')
    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number')
    shape = fields.Char('Shape')
    size = fields.Float('Size (mm)')
    area = fields.Float('Area (mm^2)')
    lo = fields.Float('Lo (mm)')
    le = fields.Float('Le (mm)')
    lc = fields.Float('Lc (mm)')
    lu = fields.Float('Lu (mm)')
    a_percent = fields.Float('A (%)')
    final_size = fields.Float('Final Size (mm^2)')
    z_percent = fields.Float('Z (%)')
    rm = fields.Float('Rm (Mpa)')
    reh = fields.Float('ReH (Mpa)')
    rel = fields.Float('ReL (Mpa)')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need Improvement'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default= lambda self: self.env.company.id)

    attachment_ids = fields.Many2many('ir.attachment', string='Attachment')

    approval_ids = fields.One2many('approval.request', 'tensile_testing_id', string='Approval')
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count')
    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for record in self:
            record.approval_count = len(record.approval_ids)

    def action_show_approval(self):
        self.ensure_one()
        if self.approval_count == 0:
            return
        action = self.env.ref('tensile_testing').ref()[0]
        action['domain'] = [('id', 'in', self.approval_ids.ids)]
        return action

    def generate_approval_request(self):
        self.ensure_one()
        category_pr = self.env.ref('tensile_testing.approval_category_data_tensile_testing')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'tensile_testing_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.user_id.name} \n Inspection for DO {self.picking_id.name}"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'requested'
        })
        request = self.approval_ids[self.approval_count-1]
        request.action_confirm()

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('tensile.testing')
        return super().create(vals)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_process(self):
        self.ensure_one()
        self.write({ 'state': 'process' })

    def action_requested(self):
        self.ensure_one()
        self.write({ 'state': 'requested' })

    def action_approved(self):
        self.ensure_one()
        self.write({ 'state': 'approved' })

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })