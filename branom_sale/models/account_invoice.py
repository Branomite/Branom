from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_zero_comm = fields.Boolean(string='Allow Zero for Commission Type',
                                  help='Set True to allow this account to zero out the balances for Journal Entries.')


class AccountMove(models.Model):
    _inherit = 'account.move'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountMove, self).finalize_invoice_move_lines(move_lines)
        # Zero out the JE if the SO is commission type
        if self.invoice_line_ids.mapped('sale_line_ids.order_id').sales_type == 'commission':
            zero_ml = []
            for move in res:
                if self.env['account.account'].browse(move[2]['account_id']).is_zero_comm:
                    temp_dict = move[2]
                    temp_dict['credit'] = False
                    temp_dict['debit'] = False
                    zero_ml.append(move[:2]+(temp_dict,))
                else:
                    zero_ml.append(move)
            return zero_ml
        return res

    @api.onchange('pricelist_id', 'invoice_line_ids')
    def apply_pricelist(self):
        for inv in self:
            if inv.pricelist_id.discount_policy != "without_discount" and inv.pricelist_id:
                raise UserError(
                    _('Selected Pricelist\'s Discount Policy must be "Show public price & discount to the customer".\n')
                )

            for line in inv.invoice_line_ids:
                if not (line.product_id and line.uom_id and self.pricelist_id and
                        self.pricelist_id.discount_policy == 'without_discount'):
                    return
                line.discount = 0.0
                
                product_context = dict(line.env.context, partner_id=self.partner_id.id,
                                       date=self.invoice_date, uom=line.uom_id.id)
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


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        if res.sale_line_ids.filtered(lambda s: s.order_id.sales_type == 'commission') and res.company_id.commission_account_id and not res.display_type:
            res.account_id = res.company_id.commission_account_id
        return res
