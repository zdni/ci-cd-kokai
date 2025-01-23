from odoo import _, api, fields, models


class ListOfDocuments(models.Model):
    _name = 'list.of.documents'
    _description = 'List Of Documents'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    department_id = fields.Many2one('hr.department', string='Department')
    team_id = fields.Many2one('department.team', string='Section', domain="[('department_id', '=', department_id)]")
    name = fields.Char('Serial Number', required=True)
    init_edition = fields.Integer('Init Edition', default=0, tracking=True)
    edition = fields.Integer('Edition/Revision No.', tracking=True, compute='_compute_amendment_count')
    description = fields.Text('Description')
    issued_date = fields.Date('Issued Date', required=True, tracking=True)
    received_date = fields.Date('Received Date', tracking=True)
    amendment_ids = fields.One2many('amendment.document', 'document_id', string='Amendments')
    amendment_count = fields.Integer('Amendment Count', compute="_compute_amendment_count")
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('amendment', 'Amendment'),
        ('refused', 'Refused'),
        ('canceled', 'Canceled'),
    ], string='Stage', default='approved', required=True, tracking=True)
    state = fields.Selection([
        ('new', 'New'),
        ('revision', 'Revision'),
        ('obsolete', 'Obsolete'),
    ], string='State', default='new', required=True, tracking=True, compute='_compute_state', store=True)
    type = fields.Selection([
        ('qm', 'Quality Manual'),
        ('qp', 'Quality Procedure'),
        ('qr', 'Quality Record'),
        ('wi', 'Work Instruction'),
    ], string='Type', default='qr', required=True)
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment')

    @api.depends('amendment_ids.state')
    def _compute_amendment_count(self):
        for record in self:
            amendment_count = len(record.mapped('amendment_ids').filtered(lambda x: x.state == 'approved')) or 0
            record.amendment_count = amendment_count
            record.edition = record.init_edition + amendment_count

    def action_show_amendment(self):
        self.ensure_one()
        action = self.env.ref('list_of_documents.amendment_document_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.amendment_ids.ids)]
        return action

    def action_obsolete(self):
        self.ensure_one()
        self.write({ 'state': 'obsolete' })
    
    @api.depends('edition')
    def _compute_state(self):
        for record in self:
            record.state = 'revision' if record.edition > 0 else 'new'