from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_zero_comm = fields.Boolean(string='Allow Zero for Commission Type',
                                  help='Set True to allow this account to zero out the balances for Journal Entries.')


class AccountMove(models.Model):
    _inherit = 'account.move'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        commission_moves = self.filtered(lambda m: any(o.sales_type == 'commission' for o in m.mapped('invoice_line_ids.sale_line_ids.order_id')))
        return super(AccountMove, (self-commission_moves))._stock_account_prepare_anglo_saxon_out_lines_vals()

    @api.onchange('pricelist_id', 'invoice_line_ids')
    def apply_pricelist(self):
        for inv in self:
            if inv.pricelist_id.discount_policy != "without_discount" and inv.pricelist_id:
                raise UserError(
                    _('Selected Pricelist\'s Discount Policy must be "Show public price & discount to the customer".\n')
                )

            for line in inv.invoice_line_ids:
                if not (line.product_id and line.product_uom_id and self.pricelist_id and
                        self.pricelist_id.discount_policy == 'without_discount'):
                    return
                line.discount = 0.0
                
                product_context = dict(line.env.context, partner_id=self.partner_id.id,
                                       date=self.invoice_date, uom=line.product_uom_id.id)
                # Must pass in SO Unit Price to keep unit price consistent when calculating the discount.
                price, rule_id = self.pricelist_id.with_context(product_context).inv_get_product_price_rule(
                    line.product_id, line.quantity or 1.0, self.partner_id, line.price_unit)

                # Set new_list_price to be the line's unit price.
                # This is always the same as it is pulled from SO not template
                new_list_price = line.price_unit

                if new_list_price != 0.0:
                    if self.pricelist_id.currency_id != line.currency_id:
                        # We need new_list_price in the same currency as price,
                        # which is in the SO's pricelist's currency
                        new_list_price = line.currency_id._convert(
                            new_list_price, self.pricelist_id.currency_id,
                            self.company_id, self.invoice_date or fields.Date.today())
                    discount = ((new_list_price - price) / new_list_price) * 100.0
                    if (discount > 0.0 and new_list_price > 0.0) or (discount < 0.0 and new_list_price < 0.0):
                        line.discount = discount
                        # changes fields related to the new unit price/discount
                        line._onchange_price_subtotal()
            # remakes offset lines
            inv._onchange_invoice_line_ids()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        for line in res:
            if line.sale_line_ids.filtered(lambda s: s.order_id.sales_type == 'commission') and line.company_id.commission_account_id and not line.display_type:
                line.account_id = line.company_id.commission_account_id
        return res
