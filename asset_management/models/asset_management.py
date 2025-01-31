from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_asset = fields.Boolean('Is Asset')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_asset = fields.Boolean('Is Asset', related='product_tmpl_id.is_asset')


class EquipmentCategory(models.Model):
    _name = 'equipment.category'
    _description = 'Equipment Category'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name', required=True)


class EquipmentAsset(models.Model):
    _name = 'equipment.asset'
    _description = 'Equipment Asset'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id, tracking=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', tracking=True)

    name = fields.Char('Name', required=True, default='New', tracking=True)
    category_id = fields.Many2one('equipment.category', string='Category', tracking=True)
    product_id = fields.Many2one('product.product', string='Product', domain="[('is_asset','=',True)]", tracking=True)
    qty = fields.Integer('Qty', tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UoM', tracking=True)
    lot_id = fields.Many2one('stock.lot', string='Lot', domain="[('product_id','=',product_id)]", tracking=True)
    used_by = fields.Selection([
        ('department', 'Department'), 
        ('employee', 'Employee'), 
        ('location', 'Location'), 
        ('other', 'Other'), 
    ], string='Used By', required=True, default='employee', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    work_location_id = fields.Many2one('hr.work.location', string='Work Location', tracking=True)
    detail_used_by = fields.Char('Detail Used By', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assign'),
        ('maintenance', 'Maintenance'),
        ('return', 'Return'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft', tracking=True)
    note = fields.Text('Note')
    assign_date = fields.Datetime('Assign Date')
    return_Date = fields.Datetime('Return Date')

    maintenance_ids = fields.One2many('helpdesk.ticket', 'asset_id', string='Maintenance')
    maintenance_count = fields.Integer('Maintenance Count', compute='_compute_maintenance_count', store=True)
    @api.depends('maintenance_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_ids)

    def action_show_maintenance(self):
        self.ensure_one()
        if self.maintenance_count == 0:
            return
        
        action = self.env.ref('helpdesk_maintenance.helpdesk_ticket_view_kanban').sudo().read()[0]
        action['domain'] = [('asset_id', '=', self.id)]
        return action

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('equipment.asset')
        return super(EquipmentAsset, self).create(vals)

    @api.onchange('used_by')
    def _onchange_used_by(self):
        for record in self:
            record.responsible_id = False
            detail_used_by = ''
            if record.used_by == 'department':
                detail_used_by = record.department_id.name
            elif record.used_by == 'employee':
                detail_used_by = record.employee_id.name
                record.responsible_id = record.employee_id.user_id.id
            elif record.used_by == 'location':
                detail_used_by = record.work_location_id.name
            record.detail_used_by = detail_used_by

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_assign(self):
        self.ensure_one()
        self.write({ 'state': 'assign', 'assign_date': fields.Datetime.now() })

    def action_maintenance(self):
        self.ensure_one()
        self.write({ 'state': 'maintenance' })

    def action_return(self):
        self.ensure_one()
        self.write({ 'state': 'return', 'return_date': fields.Datetime.now() })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    asset_id = fields.Many2one('equipment.asset', string='Asset')