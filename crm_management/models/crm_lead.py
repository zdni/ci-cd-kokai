from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

CODE_CONTRACT = {
    'tender': 'contract.review.a',
    'retail': 'contract.review.c',
}


class MinutesMeeting(models.Model):
    _inherit = 'minutes.meeting'

    lead_id = fields.Many2one('crm.lead', string='Lead')
    crm_stage = fields.Char('Stage CRM')
    crm_state = fields.Char('State CRM')


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    source = fields.Selection([
        ('tender', 'Tender'),
        ('retail', 'Retail'),
    ], string='Source', default='retail')
    state = fields.Selection([
        ('new', 'New'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ('lost', 'Lost'),
    ], string='State', default='new', required=True, tracking=True)
    team_id = fields.Many2one('crm.team', string='Sales Team', ondelete='restrict')
    history_ids = fields.One2many('stage.history', 'lead_id', string='History')
    scope_ids = fields.Many2many('product.tag', string='Scope')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    attachment_ids = fields.Many2many('ir.attachment', string='Files')
    sm_team_id = fields.Many2one('department.team', string='Sales Team')
    pic_ids = fields.Many2many('res.partner', string='PIC')

    def action_view_stage_change_wizard(self):
        self.ensure_one()
        ctx = dict(default_ref_id=self.id, active_ids=self.ids)
        return {
            'name': _('Change Stage'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stage.change.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }

    def generate_new_inquiry(self):
        self.ensure_one()
        inquiry_number = self.env['ir.sequence'].sudo().next_by_code('inquiry.review')
        val = {
            'name': inquiry_number,
            'partner_id': self.partner_id.id,
            'source': self.source,
            'frk_type': 'a' if self.source == 'tender' else 'c',
            'tag_ids': self.tag_ids.ids,
            'lead_id': self.id,
            'revision': self.inquiry_count+1,
            'inquiry_date': fields.Date.today(),
            'state': 'inquiry',
            'team_id': self.team_id.id,
            'account_executive_id': self.user_id.id,
            'user_id': self.salesperson_id.id,
            'manager_id': self.team_id.user_id.id,
            'scope': self.name,
            'due_date': self.date_deadline,
        }
        self.write({ 'order_ids': [(0, 0, val)], 'inquiry_number': inquiry_number, 'state': 'process' })
        inquiry = self.order_ids[self.inquiry_count-1]
        if inquiry:
            inquiry.generate_project_requirements()

    def generate_quotation(self):
        self.ensure_one()
        code = CODE_CONTRACT[self.source]
        # contract_number = self.env['ir.sequence'].sudo().next_by_code(code)
        quotation_number = self.env['ir.sequence'].sudo().next_by_code('quotation.order')
        inquiry = self.order_ids[self.inquiry_count-1]
        if inquiry.inquiry_state == 'done':
            inquiry.write({
                'name': quotation_number,
                'state': 'draft',
                'is_frk': False,
            })
            self.write({ 'state': 'process' })

    def generate_frk(self):
        self.ensure_one()
        code = CODE_CONTRACT[self.source]
        contract_number = self.env['ir.sequence'].sudo().next_by_code(code)
        inquiry = self.order_ids[self.inquiry_count-1]
        if inquiry.inquiry_state == 'done':
            inquiry.write({
                'name': contract_number,
                'state': 'draft',
            })
            inquiry.action_confirm()
            inquiry.set_as_frk()
            self.write({ 'state': 'process' })

    def notification_change_stage(self):
        self.ensure_one()
        try:
            notification = self.env['assignment.task'].create({
                'type': 'notification',
                'subject': 'Notification about change Stage of Lead',
                'user_id': self.env.user.id,
                'assigned_to': 'employee',
                'user_ids': self.sm_team_id.member_ids.ids,
                'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
                'description': f"Notification about change stage of Lead {self.name} to {self.stage_id.name}",
                'date': fields.Date.today(),
                'start_date': fields.Datetime.now(),
                'stop_date': fields.Datetime.now(),
                'model': 'crm.lead',
                'res_id': self.id,
            })
            notification.action_assign()
        except:
            raise ValidationError("Can't Send Notification to User. Please Contact Administrator!")
                
    inquiry_number = fields.Char('Inquiry Number', default='New')
    inquiry_count = fields.Integer('Inquiry Count', compute='_compute_inquiry_count', default=0)
    @api.depends('order_ids', 'order_ids.state')
    def _compute_inquiry_count(self):
        self.ensure_one()
        self.inquiry_count = len([inquiry for inquiry in self.order_ids if inquiry.state == 'inquiry'])

    quotation_count = fields.Integer('Quotation Count', compute='_compute_quotation_count', default=0)
    @api.depends('order_ids', 'order_ids.state')
    def _compute_quotation_count(self):
        self.ensure_one()
        self.quotation_count = len([order for order in self.order_ids if order.state == 'draft'])

    contract_count = fields.Integer('Contract Count', compute='_compute_contract_count', default=0)
    @api.depends('order_ids', 'order_ids.state')
    def _compute_contract_count(self):
        self.ensure_one()
        self.contract_count = len([order for order in self.order_ids if order.state in ['sale', 'done', 'issue']])

    def action_show_inquiry(self):
        if self.inquiry_count == 0:
            return
        action = (self.env.ref('crm_management.inquiry_review_action').sudo().read()[0])
        action['domain'] = [('id', 'in', self.order_ids.ids), ('state', '=', 'inquiry')]
        return action

    def action_show_quotation(self):
        if self.quotation_count == 0:
            return
        action = (self.env.ref('sale.action_quotations_with_onboarding').sudo().read()[0])
        action['context'] = {}
        action['domain'] = [('id', 'in', self.order_ids.ids), ('state', '=', 'draft')]
        return action

    def action_show_contract(self):
        if self.contract_count == 0:
            return
        action = (self.env.ref('crm_management.contract_review_action').sudo().read()[0])
        action['domain'] = [('id', 'in', self.order_ids.ids), ('state', 'in', ['sale', 'done', 'issue'])]
        return action

    meeting_ids = fields.One2many('minutes.meeting', 'lead_id', string='Meeting')
    meeting_count = fields.Integer('Meeting Count', compute='_compute_meeting_count')
    @api.depends('meeting_ids')
    def _compute_meeting_count(self):
        for record in self:
            record.meeting_count = len(record.meeting_ids)

    def action_show_meeting(self):
        if self.meeting_count == 0:
            return
        action = (self.env.ref('minutes_of_meeting.minutes_meeting_action').sudo().read()[0])
        action['domain'] = [('id', 'in', self.meeting_ids.ids)]
        return action

    def action_view_schedule_meeting_wizard(self):
        self.ensure_one()
        ctx = dict(default_lead_id=self.id, active_ids=self.ids, default_description='Meeting with ' + self.partner_id.name, default_partner_ids=[self.partner_id.id], default_partner_id=self.partner_id.id)
        return {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'schedule.meeting.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }