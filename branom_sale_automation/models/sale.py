from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    percent_delivered = fields.Float('Delivered (%)', compute='_compute_percent_delivered', store=True)

    @api.depends('order_line.product_uom_qty', 'order_line.qty_delivered')
    def _compute_percent_delivered(self):
        for order in self:
            qty_ordered = sum(order.order_line
                              .filtered(lambda l: l.product_id.type != 'service' and not l.is_delivery)
                              .mapped('product_uom_qty'))
            qty_delivered = sum(order.order_line
                                .filtered(lambda l: l.product_id.type != 'service' and not l.is_delivery)
                                .mapped('qty_delivered'))
            if qty_ordered == 0.0:
                order.percent_delivered = -1
            else:
                order.percent_delivered = (qty_delivered / qty_ordered) * 100.0
            # if the delivery is 'essentially complete', increment delivered qty on delivery product
            if 99.5 <= order.percent_delivered <= 100.5:
                # some orders have more than one delivery line!
                delivery_lines = order.order_line.filtered(lambda l: l.is_delivery)
                for delivery_line in delivery_lines:
                    if delivery_line.product_uom_qty != delivery_line.qty_delivered:
                        delivery_line.qty_delivered = delivery_line.product_uom_qty
