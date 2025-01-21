from odoo import _, api, fields, models, http
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    request_id = fields.Many2one('purchase.request', string='Request')


class PurchaseRequestType(models.Model):
    _name = 'purchase.request.type'
    _description = 'Type of Purchase Request'

    name = fields.Char('Name', required=True)

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.model
    def _default_domain_team(self):
        return [('department_id', '=', self.env.ref('department_detail.hr_management_data_purchasing').id)]

    approver_id = fields.Many2one('res.users', string='Approver', default=lambda self: self.env.user.department_id.manager_id.user_id.id)
    department_id = fields.Many2one('hr.department', string='Department', required=True, default=lambda self: self.env.user.department_id.id)
    due_date = fields.Date('Due Date', tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'ASAP'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', required=True, default='0')
    type_id = fields.Many2one('purchase.request.type', string='Type', required=True, tracking=True)
    type = fields.Selection([
        ('project', 'Project'),
        ('non_project', 'Non Project'),
    ], string='Description', required=True, default='project', tracking=True)
    team_id = fields.Many2one('department.team', string='Purchase Team', required=True, domain=_default_domain_team, tracking=True)
    director = fields.Char('Director', related='company_id.director_id.name')

    @api.onchange('requested_by')
    def _onchange_requested_by(self):
        for record in self:
            if record.requested_by:
                employee = self.env['hr.employee'].search([
                    ('user_id', '=', record.requested_by.id),
                    ('active', '=', True),
                ], limit=1)
                if employee:
                    record.sudo().write({
                        'department_id': employee.department_id.id or False,
                        'approver_id': employee.department_id.manager_id.user_id.id or False,
                    })

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val['department_id']:
                sequence = self.env['ir.sequence.department'].search([
                    ('department_id.id', '=', val['department_id']),
                    ('model_id.model', '=', 'purchase.request'),
                ], limit=1)
                if sequence:
                    val['name'] = self.env['ir.sequence'].next_by_code(sequence.sequence_id.code)

        return super(PurchaseRequest, self).create(vals)

    def button_in_progress(self):
        # request to purchasing team
        if self.team_id:
            schedule = self.env['assignment.task'].sudo().create({
                'department_ids': [self.team_id.department_id.id],
                'user_id': self.env.user.id,
                'user_ids': self.team_id.member_ids,
                'assigned_to': 'employee',
                'subject': f"Permintaan Proses Purchase Request {self.name}",
                'description': f"Permintaan Proses Purchase Request {self.name}",
                'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
                'model': 'purchase.request',
                'res_id': self.id,
            })
            schedule.action_assign()

        super(PurchaseRequest, self).button_in_progress()

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    link = fields.Char('Link')
    reason = fields.Char('Reason')
    drawing = fields.Binary('Drawing')
    suggested = fields.Char('Item/Supplier')