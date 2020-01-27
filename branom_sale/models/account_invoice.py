# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_zero_comm = fields.Boolean(string='Allow Zero for Commission Type',
                                  help='Set True to allow this account to zero out the balances for Journal Entries.')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
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
                                       date=self.date_invoice, uom=line.uom_id.id)
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
                            self.company_id, self.date_invoice or fields.Date.today())
                    discount = ((new_list_price - price) / new_list_price) * 100.0
                    if (discount > 0.0 and new_list_price > 0.0) or (discount < 0.0 and new_list_price < 0.0):
                        line.discount = discount


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # @api.model
    # def _default_account(self):
    #     res = super(AccountInvoiceLine, self)._default_account()
    #     print("THIS account invoice line IS TRIGGERED ON INV << super of default")
    #     if self.sale_line_ids:
    #         print("We have a SO(s) tied to the account")
    #     return res

    @api.model
    def create(self, vals):
        print("THIS CREATE IS TRIGGERED ON INV LINE")
        res = super(AccountInvoiceLine, self).create(vals)
        if res.sale_line_ids.filtered(lambda s: s.order_id.sales_type == 'commission') and res.company_id.commission_account_id:
            print("Sale order is tied to the commission")
            res.account_id = res.company_id.commission_account_id
        return res

    # account_id = fields.Many2one('account.account', string='Account', domain=[('deprecated', '=', False)],
    #                              default=_default_account,
    #                              help="The income or expense account related to the selected product.")