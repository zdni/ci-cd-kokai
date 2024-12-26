from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    part_id = fields.Many2one('equipment.part', string='Part')
    return_part_id = fields.Many2one('equipment.part.return', string='Part')


class StockEquipment(models.Model):
    _name = 'stock.equipment'
    _description = 'Equipment Part Used by Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_location_dest_id(self):
        location = self.env['stock.location'].search([
            ('warehouse_id.id', '=', self.env.ref('employee_inventory.stock_warehouse_data_warehouse_employee').id),
            ('usage', '=', 'internal')
        ], limit=1)
        if location:
            return location.id
        return False

    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='Assigned By', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    
    name = fields.Char('Name', default='New')
    used_by = fields.Selection([
        ('department', 'Department'), 
        ('employee', 'Employee'), 
        ('location', 'Location'), 
        ('other', 'Other'), 
    ], string='Used By', required=True, default='employee', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    work_location_id = fields.Many2one('hr.work.location', string='Work Location', tracking=True)
    detail_used_by = fields.Char('Detail Used By')
    assigned_time = fields.Datetime('Assigned Time')
    returned_time = fields.Datetime('Returned Time')
    picking_id = fields.Many2one('stock.picking', string='Picking', tracking=True)
    location_id = fields.Many2one('stock.location', string='From', required=True, domain="[('usage', '=', 'internal')]")
    location_dest_id = fields.Many2one('stock.location', string='Location', required=True,  domain="[('usage', '=', 'internal')]", default=_default_location_dest_id)
    notes = fields.Text('Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted by Recipient'),
        ('returned', 'Returned'),
        ('canceled', 'Canceled'),
    ], string='State', default='draft', required=True, readonly=True, tracking=True, compute='_compute_state', store=True)
    @api.depends('part_ids.state')
    def _compute_state(self):
        for record in self:
            all_has_return = record.mapped('part_ids').filtered(lambda part: part.state != 'returned')
            if len(all_has_return) == 0 and len(record.part_ids) > 0:
                record.write({'state': 'returned'})

    part_ids = fields.One2many('equipment.part', 'equipment_id', string='Product')

    recipient_id = fields.Many2one('res.users', string='Recipient')
    recipient_approval = fields.Boolean('Recipient Approval')
    approval_date = fields.Datetime('Approval Date')

    return_ids = fields.One2many('stock.equipment.return', 'equipment_id', string='Return')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for record in self:
            record.recipient_id = record.employee_id.user_id.id if record.used_by == 'employee' else False
            record.detail_used_by = record.employee_id.name

    @api.onchange('department_id')
    def _onchange_department_id(self):
        for record in self:
            record.detail_used_by = record.department_id.name

    @api.onchange('work_location_id')
    def _onchange_work_location_id(self):
        for record in self:
            record.detail_used_by = record.work_location_id.name

    @api.onchange('used_by')
    def _onchange_used_by(self):
        for record in self:
            detail = ''
            if record.used_by == 'department':
                detail = record.department_id.name
            if record.used_by == 'employee':
                detail = record.employee_id.name 
            if record.used_by == 'location':
                detail = record.work_location_id.name 
            record.detail_used_by = detail 

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('stock.equipment')
        return super(StockEquipment, self).create(vals)

    def _assigned_equipment(self):
        vals = self._prepared_stock_picking(self.name, self.location_id, self.location_dest_id, self.part_ids)
        picking = self.env['stock.picking'].sudo().create(vals)
        picking.sudo().action_confirm()
        picking.sudo().action_assign()
        for line in picking.move_ids_without_package:
            move_line = self.env['stock.move.line'].search([ ('move_id', '=', line.id) ])
            move_line.write({ 'lot_id': line.part_id.lot_id.id, 'qty_done': line.product_uom_qty })
        picking.sudo().button_validate()
        self.write({ 'picking_id': picking.id })

    
    def _prepared_stock_picking(self, name, location_id, location_dest_id, part_ids):
        return {
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'origin': name,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            'move_ids_without_package': [(0 ,0, {
                'name': name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty,
                'product_uom': line.uom_id.id,
                'lot_ids': [line.lot_id.id],
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'company_id': self.env.company.id,
                'part_id': line.id,
            }) for line in part_ids]
        }

    def action_draft(self):
        self.ensure_one()
        self.part_ids.action_draft()
        self.sudo().write({ 'state': 'draft', 'assigned_time': False, 'returned_time': False })

    def action_assigned(self):
        self.ensure_one()
        self._assigned_equipment()
        self.part_ids.action_assigned()
        self.sudo().write({ 'assigned_time': fields.Datetime.now(), 'state': 'assigned' })

    def action_accepted(self):
        self.ensure_one()
        self.part_ids.action_accepted()
        self.sudo().write({ 'recipient_approval': True, 'approval_date': fields.Datetime.now(), 'state': 'accepted' })

    def action_returned(self):
        self.ensure_one()
        if not self.state == 'accepted':
            raise ValidationError("Can't Return Equipment not in Accepted by Recipient")

        vals = self._prepare_return_equipment()
        equipment_return = self.env['stock.equipment.return'].create(vals)
        # self.sudo().write({ 'returned_time': fields.Datetime.now(), 'state': 'returned' })

    def action_canceled(self):
        self.ensure_one()
        self.part_ids.action_canceled()
        self.sudo().write({ 'state': 'canceled' })
    
    def _prepare_return_equipment(self):
        return {
            'equipment_id': self.id,
            'user_id': self.recipient_id.id,
            'company_id': self.env.company.id,
            'location_id': self.location_dest_id.id,
            'location_dest_id': self.location_id.id,
            'returned_time': fields.Datetime.now(),
            'part_ids': [(0,0,{
                'part_id': line.id,
                'product_id': line.product_id.id,
                'qty': 1,
                'uom_id': line.uom_id.id,
                'condition': line.condition,
                'lot_id': line.lot_id.id,
            }) for line in self.part_ids],
            'recipient_id': self.env.user.id,
        }

    def action_show_part(self):
        self.ensure_one()
        if len(self.part_ids) == 0:
            return
        action = self.env.ref('employee_inventory.equipment_part_action').read()[0]
        action['domain'] = [('id', 'in', self.part_ids.ids)]
        return action

    def action_show_return(self):
        self.ensure_one()
        if len(self.return_ids) == 0:
            return
        action = self.env.ref('employee_inventory.stock_equipment_return_action').read()[0]
        action['domain'] = [('id', 'in', self.return_ids.ids)]
        return action


class EquipmentPart(models.Model):
    _name = 'equipment.part'
    _description = 'Equipment Product for Used by Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    equipment_id = fields.Many2one('stock.equipment', string='Equipment')

    user_id = fields.Many2one('res.users', string='Assigned By', related='equipment_id.user_id')
    company_id = fields.Many2one('res.company', string='Company', related='equipment_id.company_id')

    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True, related='equipment_id.employee_id')
    department_id = fields.Many2one('hr.department', string='Department', tracking=True, related='equipment_id.department_id')
    work_location_id = fields.Many2one('hr.work.location', string='Work Location', tracking=True, related='equipment_id.work_location_id')
    detail_used_by = fields.Char('Detail Used By', related='equipment_id.detail_used_by')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Float('Qty', default=1)
    uom_id = fields.Many2one('uom.uom', string='UoM', required=True)
    condition = fields.Selection([
        ('damaged', 'Damaged'),
        ('proper', 'Proper'),
        ('good', 'Good'),
    ], string='Condition', required=True, default='proper')
    assigned_time = fields.Datetime('Assigned Time', related='equipment_id.assigned_time')
    returned_time = fields.Datetime('Returned Time')
    lot_id = fields.Many2one('stock.lot', string='SN/Lot', domain="[('product_id', '=', product_id)]")

    return_ids = fields.Many2many('equipment.part.return', string='Return')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted by Recipient'),
        ('returned', 'Returned'),
        ('canceled', 'Canceled'),
    ], string='State', default='draft', required=True, readonly=True, compute='_compute_state', store=True)
    @api.depends('return_ids.state')
    def _compute_state(self):
        for record in self:
            qty_return = sum([part_return.qty if part_return.state == 'accepted' else 0 for part_return in record.return_ids])
            if qty_return == record.qty:
                record.state = 'returned'

    @api.model_create_multi
    def create(self, vals):
        lines = super(EquipmentPart, self).create(vals)
        for line in lines:
            msg = f"{line.product_id.display_name} has been added."
            line.equipment_id.sudo().message_post(body=msg)
        return lines

    def generate_returned_part(self):
        self.ensure_one()

    def action_draft(self):
        for record in self:
            record.sudo().write({ 'state': 'draft', 'assigned_time': False, 'returned_time': False })

    def action_assigned(self):
        for record in self:
            record.sudo().write({ 'state': 'assigned' })

    def action_accepted(self):
        for record in self:
            record.sudo().write({ 'state': 'accepted' })

    def action_returned(self):
        for record in self:
            record.sudo().write({ 'state': 'returned' })

    def action_canceled(self):
        for record in self:
            record.sudo().write({ 'state': 'canceled' })


class StockEquipmentReturn(models.Model):
    _name = 'stock.equipment.return'
    _description = 'Stock Equipment Return'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_location_id(self):
        location = self.env['stock.location'].search([
            ('warehouse_id.id', '=', self.env.ref('employee_inventory.stock_warehouse_data_warehouse_employee').id),
            ('usage', '=', 'internal')
        ], limit=1)
        if location:
            return location.id
        return False

    equipment_id = fields.Many2one('stock.equipment', string='Equipment')
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='Assigned By', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    name = fields.Char('Name', default='New')
    returned_time = fields.Datetime('Returned Time')
    picking_id = fields.Many2one('stock.picking', string='Picking', tracking=True)
    location_id = fields.Many2one('stock.location', string='From', required=True, domain="[('usage', '=', 'internal')]")
    location_dest_id = fields.Many2one('stock.location', string='Location', required=True,  domain="[('usage', '=', 'internal')]")
    notes = fields.Text('Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('returned', 'Returned'),
        ('accepted', 'Accepted by Recipient'),
        ('canceled', 'Canceled'),
    ], string='State', default='draft', required=True, readonly=True, tracking=True)

    part_ids = fields.One2many('equipment.part.return', 'return_id', string='Product')

    recipient_id = fields.Many2one('res.users', string='Recipient')
    recipient_approval = fields.Boolean('Recipient Approval')
    approval_date = fields.Datetime('Approval Date')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('stock.equipment.return')
        return super(StockEquipmentReturn, self).create(vals)

    def _returned_equipment(self):
        operation_type = self.env['stock.picking.type'].sudo().search([
            ('warehouse_id.id', '=', self.location_id.warehouse_id.id),
            ('code', '=', 'internal'),
        ], limit=1)
        if not operation_type:
            raise ValidationError('Operation Type not Found. Please contact Administrator!')
        vals = self._prepared_stock_picking(self.name, self.location_id, self.location_dest_id, self.part_ids, self.state, operation_type)
        picking = self.env['stock.picking'].sudo().create(vals)
        # picking.sudo().action_confirm()
        # picking.sudo().action_assign()
        # for line in picking.move_ids_without_package:
        #     move_line = self.env['stock.move.line'].search([ ('move_id', '=', line.id) ])
        #     move_line.write({ 'lot_id': line.part_id.lot_id.id, 'qty_done': line.product_uom_qty })
        # picking.sudo().button_validate()
        self.write({ 'picking_id': picking.id })
    
    def _prepared_stock_picking(self, name, location_id, location_dest_id, part_ids, state, operation_type):
        return {
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'origin': name,
            'picking_type_id': operation_type.id,
            'move_ids_without_package': [(0 ,0, {
                'name': name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.qty,
                'product_uom': line.uom_id.id,
                'lot_ids': [line.lot_id.id],
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'company_id': self.env.company.id,
                'return_part_id': line.id,
            }) for line in part_ids if line.state == state]
        }

    def action_draft(self):
        self.ensure_one()
        self.sudo().write({ 'state': 'draft', 'returned_time': False })

    def action_returned(self):
        self.ensure_one()
        self._returned_equipment()
        self.sudo().write({ 'returned_time': fields.Datetime.now(), 'state': 'returned' })

    def action_accepted(self):
        self.ensure_one()
        self.sudo().write({ 'recipient_approval': True, 'approval_date': fields.Datetime.now(), 'state': 'accepted' })

    def action_canceled(self):
        self.ensure_one()
        self.sudo().write({ 'state': 'canceled' })


class EquipmentPartReturn(models.Model):
    _name = 'equipment.part.return'
    _description = 'Return Equipment Product from Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    return_id = fields.Many2one('stock.equipment.return', string='Equipment Return')
    part_id = fields.Many2one('equipment.part', string='Part')

    user_id = fields.Many2one('res.users', string='User', related='return_id.user_id')
    company_id = fields.Many2one('res.company', string='Company', related='return_id.company_id')

    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Float('Qty', default=1)
    uom_id = fields.Many2one('uom.uom', string='UoM', required=True)
    lot_id = fields.Many2one('stock.lot', string='SN/Lot', domain="[('product_id', '=', product_id)]")
    condition = fields.Selection([
        ('damaged', 'Damaged'),
        ('proper', 'Proper'),
        ('good', 'Good'),
    ], string='Condition', required=True, default='proper')
    returned_time = fields.Datetime('Returned Time', related='return_id.returned_time')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('returned', 'Returned'),
        ('accepted', 'Accepted by Recipient'),
        ('canceled', 'Canceled'),
    ], string='State', default='draft', required=True, readonly=True, related='return_id.state')