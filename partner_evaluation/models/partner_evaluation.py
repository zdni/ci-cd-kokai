from odoo import _, api, fields, models

class PartnerEvaluation(models.Model):
    _name = 'partner.evaluation'
    _description = 'Form of Partner Evaluation'

    @api.depends('template_id')
    def _compute_title(self):
        for record in self:
            record.title = record.template_id.name or ''

    template_id = fields.Many2one('evaluation.template', string='Template', required=True)
    name = fields.Char('Name', default='New')
    title = fields.Char('Title', compute='_compute_title')
    evaluation_date = fields.Datetime('Evaluation Date')
    due_date = fields.Datetime('Due Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled'),
    ], string='State', default='draft')
    user_ids = fields.Many2many('res.users', string='Auditor(s)', default=lambda self: [self.env.user.id])
    partner_id = fields.Many2one('res.partner', string='Partner')
    result_ids = fields.One2many('evaluation.result', 'evaluation_id', string='Results')
    note = fields.Text('Note')
    conclusion = fields.Text('Conclusion')
    total_point = fields.Integer('Total Point', compute='_compute_total_point')
    average_point = fields.Float('Average Point', compute='_compute_average_point')
    classification = fields.Selection([
        ('critical', 'Critical'),
        ('non_critical', 'Non-Critical'),
    ], string='Classification Product')
    product_ids = fields.Many2many('product.product', string='Products')
    total_employee = fields.Integer('Total Employee', default=1)
    type = fields.Selection([
        ('init', 'Initial Evaluation'),
        ('reval', 'Re-Evaluation'),
    ], string='Type', default='init', required=True)

    approval_ids = fields.One2many('approval.request', 'evaluation_id', string='Approval')
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count')

    @api.depends('result_ids')
    def _compute_total_point(self):
        for record in self:
            total_point = sum([evaluation.item_id.score for evaluation in record.result_ids])
            record.total_point = total_point

    @api.depends('total_point')
    def _compute_average_point(self):
        for record in self:
            record.average_point = record.total_point/len(record.result_ids) if len(record.result_ids) > 0 else 0

    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for record in self:
            record.approval_count = len(record.approval_ids)

    def action_show_approval_request(self):
        pass

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('name') == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('partner.evaluation')
        return super(PartnerEvaluation, self).create(vals)

    def generate_question_from_template(self):
        for record in self:
            record.write({ 'result_ids': [(0,0,{
                'evaluation_id': record.id,
                'question_id': line.id,
                'category_id': line.category_id.id,
            }) for line in record.template_id.line_ids ] })


class EvaluationResult(models.Model):
    _name = 'evaluation.result'
    _description = 'Result from Partner Evaluation'

    evaluation_id = fields.Many2one('partner.evaluation', string='Evaluation', required=True)
    question_id = fields.Many2one('evaluation.question', string='Question', required=True)
    category_id = fields.Many2one('evaluation.category', string='Category', required=True)
    item_id = fields.Many2one('evaluation.item', string='Item')
    score = fields.Integer('Score', compute='_compute_score')
    remark = fields.Text('Remark')

    @api.depends('item_id')
    def _compute_score(self):
        for record in self:
            record.score = record.item_id.score