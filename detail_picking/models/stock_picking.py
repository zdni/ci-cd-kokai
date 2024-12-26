from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_show_all_picking(self):
        self.ensure_one()
        pickings = self.env['stock.picking'].search([ ('group_id', '=', self.group_id.id) ])
        if len(pickings) == 0:
            return

        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('id', 'in', pickings.ids)]
        return action


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_show_all_picking(self):
        self.ensure_one()
        pickings = self.env['stock.picking'].search([ ('group_id', '=', self.procurement_group_id.id) ])
        if len(pickings) == 0:
            return

        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('id', 'in', pickings.ids)]
        return action