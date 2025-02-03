from odoo import _, api, fields, models, Command, _
from odoo.exceptions import UserError
from odoo.tools import email_split, float_is_zero, float_repr, float_compare, is_html_empty
from odoo.tools.misc import clean_context, format_date
import logging


_logger = logging.getLogger(__name__)




class HrExpense(models.Model):
    _inherit = 'hr.expense'

    team_id = fields.Many2one('department.team', string='Team')
    state = fields.Selection(selection_add=[('request', 'Request'), ('need_improvement', 'Need Improvement')], string='Status')
    approval_ids = fields.One2many(comodel_name='approval.request', inverse_name='expense_id', string='Approval Request', readonly=True, copy=False, tracking=True)
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count', readonly=True)
    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(rec.mapped('approval_ids'))

    def _send_notification_to_team(self):
        self.ensure_one()
        if self.team_id:
            schedule = self.env['assignment.task'].sudo().create({
                'department_ids': [self.team_id.department_id.id],
                'user_id': self.env.user.id,
                'user_ids': self.team_id.member_ids,
                'assigned_to': 'employee',
                'subject': f"Notifikasi Request Expense {self.name}",
                'description': f"Notifikasi Request Expense {self.name}",
                'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
                'model': 'hr.expense',
                'res_id': self.id,
            })
            schedule.action_assign()

    def generate_approval_request(self):
        self.ensure_one()
        self._send_notification_to_team()
        category_pr = self.env.ref('approvals_expense.approval_category_data_expense')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'expense_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.employee_id.name} \n {self.description}"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'request'
        })
        request = self.approval_ids[self.approval_count-1]
        # approver = self.env['approval.approver'].search([
        #     ('request_id.id', '=', request.id),
        #     ('user_id.id', '=', 2),
        # ])
        # if approver:
        #     approver.sudo().write({ 'user_id': self.employee_id.parent_id.user_id.id })
        request.action_confirm()

    def action_view_approval_request(self):
        action = (self.env.ref('approvals.approval_request_action_all').sudo().read()[0])
        approvals = self.mapped('approval_ids')
        if len(approvals) > 1:
            action['domain'] = [('id', 'in', approvals.ids)]
        elif approvals:
            action['views'] = [(self.env.ref('approvals.approval_request_view_form').id, 'form')]
            action['res_id'] = approvals.ids[0]
        return action

    def action_approved(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approve Expense',
            'user_id': self.employee_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.employee_id.name} \n Expense {self.name} yang diajukan telah disetujui. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'hr.expense',
            'res_id': self.id,
        })
        self.with_context(forced_create=True).action_submit_expenses()
        self.sheet_id.write({ 'state': 'approve' })
        # self.sheet_id.write({ 'user_id': self.env.user.id })
        # self.sheet_id.action_submit_sheet()
        # self.sheet_id.approve_expense_sheets()
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Expense',
            'user_id': self.employee_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.employee_id.name} \n Expense {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'hr.expense',
            'res_id': self.id,
        })
        notification.action_assign()

    def _get_default_expense_sheet_values(self):
        # If there is an expense with total_amount_company == 0, it means that expense has not been processed by OCR yet
        expenses_with_amount = self.filtered(lambda expense: not float_compare(expense.total_amount_company, 0.0, precision_rounding=expense.company_currency_id.rounding) == 0)

        if any(expense.state not in ['draft', 'request'] or expense.sheet_id for expense in expenses_with_amount):
            raise UserError(_("You cannot report twice the same line!"))
        if not expenses_with_amount:
            raise UserError(_("You cannot report the expenses without amount!"))
        if len(expenses_with_amount.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in expenses_with_amount):
            raise UserError(_("You can not create report without category."))
        if len(self.company_id) != 1:
            raise UserError(_("You cannot report expenses for different companies in the same report."))

        # Check if two reports should be created
        own_expenses = expenses_with_amount.filtered(lambda x: x.payment_mode == 'own_account')
        company_expenses = expenses_with_amount - own_expenses
        create_two_reports = own_expenses and company_expenses

        sheets = [own_expenses, company_expenses] if create_two_reports else [expenses_with_amount]
        values = []

        # We use a fallback name only when several expense sheets are created,
        # else we use the form view required name to force the user to set a name
        for todo in sheets:
            paid_by = 'company' if todo[0].payment_mode == 'company_account' else 'employee'
            sheet_name = _("New Expense Report, paid by %(paid_by)s", paid_by=paid_by) if len(sheets) > 1 else False
            if len(todo) == 1:
                sheet_name = todo.name
            else:
                dates = todo.mapped('date')
                if False not in dates:  # If at least one date isn't set, we don't set a default name
                    min_date = format_date(self.env, min(dates))
                    max_date = format_date(self.env, max(dates))
                    if min_date == max_date:
                        sheet_name = min_date
                    else:
                        sheet_name = _("%(date_from)s - %(date_to)s", date_from=min_date, date_to=max_date)

            vals = {
                'company_id': self.company_id.id,
                'employee_id': self[0].employee_id.id,
                'name': sheet_name,
                'expense_line_ids': [Command.set(todo.ids)],
                'state': 'draft',
            }
            values.append(vals)
        _logger.warning(values)
        return values

    def action_submit_expenses(self):
        self.ensure_one()
        if self._context.get('forced_create'):
            context_vals = self._get_default_expense_sheet_values()
            sheets = self.env['hr.expense.sheet'].create(context_vals)
            return {
                'name': _('New Expense Reports'),
                'type': 'ir.actions.act_window',
                'views': [[False, "list"], [False, "form"]],
                'res_model': 'hr.expense.sheet',
                'domain': [('id', 'in', sheets.ids)],
                'context': self.env.context,
            }
        else:
            return super(HrExpense, self).action_submit_expenses()