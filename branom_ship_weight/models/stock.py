from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_weight = fields.Float('Weight', digits='Stock Weight', related='product_id.weight', readonly=False)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_weight = fields.Float('Weight', digits='Stock Weight', related='product_id.weight', readonly=False)
