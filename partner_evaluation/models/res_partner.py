from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    evaluation_ids = fields.One2many('partner.evaluation', 'partner_id', string='Evaluation')
    evaluation_count = fields.Integer('Evaluation Count', compute='_compute_evaluation_count')
    evaluation = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('blacklist', 'Blacklist'),
    ], string='Evaluation', default='draft', required=True)

    @api.depends('evaluation_ids')
    def _compute_evaluation_count(self):
        for record in self:
            record.evaluation_count = len(record.evaluation_ids)

    def action_show_partner_evaluation(self):
        evaluations = self.mapped('evaluation_ids')
        if len(evaluations) == 0:
            return
        
        action = (self.env.ref('partner_evaluation.partner_evaluation_action').sudo().read()[0])
        if len(evaluations) > 1:
            action['domain'] = [('id', 'in', evaluations.ids), ('state', '=', 'inquiry')]
        elif evaluations:
            action['views'] = [(self.env.ref('partner_evaluation.partner_evaluation_view_form').id, 'form')]
            action['res_id'] = evaluations.ids[0]
        return action

    def generate_evaluation_wizard(self):
        ctx = dict(default_partner_id=self.id)
        return {
            'name': _('Generate Evaluation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'generate.evaluation.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }