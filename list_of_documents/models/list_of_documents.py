from odoo import _, api, fields, models


class ListOfDocuments(models.Model):
    _name = 'list.of.documents'
    _description = 'List Of Documents'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    department_id = fields.Many2one('hr.department', string='Department')
    team_id = fields.Many2one('department.team', string='Team', domain="[('department_id', '=', department_id)]")
    code = fields.Char('Code')
    name = fields.Char('Serial Number', required=True)
    init_edition = fields.Char('Init Edition', default=0, tracking=True)
    edition = fields.Char('Edition/Revision No.', tracking=True, compute='_compute_amendment_count', store=True)
    curr_edition = fields.Integer('Int Edition', compute='_compute_amendment_count')
    description = fields.Text('Description')
    issued_date = fields.Date('Issued Date', required=True, tracking=True)
    received_date = fields.Date('Effective Date', tracking=True)
    amendment_ids = fields.One2many('amendment.document', 'document_id', string='Amendments')
    amendment_count = fields.Integer('Amendment Count', compute="_compute_amendment_count", store=True, default=0)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    stage = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Applicable'),
        ('amendment', 'Amendment'),
        ('refused', 'Refused'),
        ('canceled', 'Canceled'),
    ], string='Stage', default='draft', required=True, tracking=True)
    state = fields.Selection([
        ('new', 'New'),
        ('revision', 'Revision'),
        ('obsolete', 'Obsolete'),
    ], string='State', default='new', required=True, tracking=True)
    source = fields.Selection([
        ('internal', 'Internal Document'),
        ('external', 'External Document'),
    ], string='Source', default='internal', required=True)
    type = fields.Selection([
        ('qm', 'Quality Manual'),
        ('qp', 'Quality Procedure'),
        ('qr', 'Quality Record'),
        ('wi', 'Work Instruction'),
        ('external', 'External Document'),
    ], string='Type', default='qr', required=True)
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment')

    def name_get(self):
        res = []
        for document in self:
            display_name = document.name + document.edition
            res.append((document.id, display_name))
        return res

    @api.depends('amendment_ids.state')
    def _compute_amendment_count(self):
        for record in self:
            if record.amendment_count > 0:
                if record.source == 'internal':
                    amendment_count = len(record.mapped('amendment_ids').filtered(lambda x: x.state == 'approved')) or 0
                    record.amendment_count = amendment_count
                    curr_edition = int(record.init_edition) + amendment_count
                    record.edition = str(curr_edition)
                    record.curr_edition = curr_edition
                else:
                    record.edition = record.init_edition
            else:
                record.edition = record.init_edition

    def action_show_amendment(self):
        self.ensure_one()
        action = self.env.ref('list_of_documents.amendment_document_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.amendment_ids.ids)]
        return action

    def action_obsolete(self):
        self.ensure_one()
        self.write({ 'state': 'obsolete' })