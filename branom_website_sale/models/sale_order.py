from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_service_product = fields.Boolean(string='Contains Service Product', compute='_compute_has_service_product')

    @api.depends('order_line.product_uom_qty', 'order_line.product_id')
    def _compute_has_service_product(self):
        for order in self:
            order.has_service_product = any(l.product_id.type == 'service' for l in order.order_line)
