from odoo import _, api, fields, models


class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')


class WorkActivity(models.Model):
    _name = 'work.activity'
    _description = 'Work Activity'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='user_id.employee_id')
    department_id = fields.Many2one('hr.department', string='Department', related='user_id.department_id')
    location_id = fields.Many2one('hr.work.location', string='Location', tracking=True)
    area_id = fields.Many2one('hr.work.area', string='Area', domain="[('location_id', '=', location_id)]", tracking=True)
    activity_id = fields.Many2one('department.activity', string='Activity', domain="[('department_id', '=', department_id)]", tracking=True)
    description = fields.Text('Description', tracking=True)
    machine_id = fields.Many2one('machine.tool', string='Machine') # machine
    # product
    # sale order
    # manufacturing order
    work_order_id = fields.Many2one('work.order', string='Work Order', tracking=True) # work order
    qty = fields.Float('Total Qty')
    qty_defect = fields.Float('Qty Defect')
    date = fields.Date('Date', default=fields.Date.today())
    start_date = fields.Datetime('Start Date', default=fields.Datetime.now())
    end_date = fields.Datetime('End Date')
    hour_spent = fields.Float('Hour Spent')
    timesheet_id = fields.Many2one('account.analytic.line', string='Timesheet')
    img_before_activity = fields.Image('Image Before Activity', max_width=100, max_height=100)
    img_after_activity = fields.Image('Image After Activity', max_width=100, max_height=100)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('work.activity')
        return super(WorkActivity, self).create(vals)

    def generate_timesheet(self):
        for record in self:
            vals = {}
            timesheet = self.env['account.analytic.line'].create(vals)
            record.write({ 'timesheet_id': timesheet.id })