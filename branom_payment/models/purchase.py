from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move):
        values = super()._prepare_account_move_line(move)
        if self.product_id and self.product_id.exclude_discount:
            values['exclude_discount'] = True
        return values
