from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_weight = fields.Float('Weight', digits='Stock Weight', related='product_id.weight', readonly=False)
