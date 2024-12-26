from odoo import _, api, fields, models


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    query_count = fields.Integer('Query Count', compute='_compute_query_count', store=True)
    @api.depends('order_ids.query_ids')
    def _compute_query_count(self):
        for record in self:
            queries = self.env['price.query'].search([ ('lead_id', '=', record.id) ])
            record.query_count = len(queries)

    def action_show_price_query(self):
        self.ensure_one()
        if self.query_count == 0:
            return
        queries = self.env['price.query'].search([ ('lead_id', '=', self.id) ])
        action = (self.env.ref('price_query.price_query_action').sudo().read()[0])
        action['domain'] = [('id', '=', queries.ids)]
        return action

    def action_stage_price_query(self):
        self.ensure_one()
        self.write({ 'stage_id': self.env.ref('price_query.crm_stage_data_price_query').id })


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    query_ids = fields.One2many('price.query', 'inquiry_id', string='Price Query')
    query_count = fields.Integer('Query Count', compute='_compute_query_count', store=True)
    @api.depends('query_ids')
    def _compute_query_count(self):
        for record in self:
            record.query_count = len(record.query_ids)

    def action_show_price_query(self):
        self.ensure_one()
        if self.query_count == 0:
            return
        action = (self.env.ref('price_query.price_query_action').sudo().read()[0])
        action['domain'] = [('id', '=', self.query_ids.ids)]
        return action

    def generate_price_query(self):
        for record in self:
            val = {
                'inquiry_id': record.id,
                'user_id': self.env.user.id,
                'lead_id': record.lead_id.id,
                'line_ids': [(0,0,{
                    'line_id': line.id,
                    'product_id': line.product_id.id,
                    'product_tmpl_id': line.product_template_id.id,
                    'qty': line.product_uom_qty,
                    'uom_id': line.product_uom.id,
                    'variant_ids': [(0,0,{
                        'attribute_id': attribute.attribute_id.id,
                        'product_tmpl_value_ids': [attribute.id]
                    }) for attribute in line.product_id.product_template_variant_value_ids],
                    'new_request': False
                }) for line in record.order_line]
            }
            record.write({ 'query_ids': [(0, 0, val)] })
            record.lead_id.action_stage_price_query()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pq_line_id = fields.Many2one('price.query.line', string='PQ Line')