from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_difference = fields.Monetary(string='Payment Difference', help="Payment difference in invoice's currency.", copy=False)
    amount_discounted_signed = fields.Monetary(string='To Be Discounted Amount in Invoice Currency', currency_field='currency_id',
        compute='_compute_amount_with_discount', store=True)
    amount_discounted_company_signed = fields.Monetary(string='To Be Discounted Amount in Company Currency', currency_field='company_currency_id',
        compute='_compute_amount_with_discount', store=True)
    # surely it's debatable if we need these two fields, 
    # but I would rather keep them in case for easy debugging in the future
    # plus it makes the payment computation much easier later
    amount_undiscounted_signed = fields.Monetary(string='Undiscounted Amount in Invoice Currency', currency_field='currency_id',
        compute='_compute_amount_with_discount', store=True)
    amount_undiscounted_company_signed = fields.Monetary(string='Undiscounted Amount in Company Currency', currency_field='company_currency_id',
        compute='_compute_amount_with_discount', store=True)

    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.exclude_discount',
                 'currency_id', 'company_id', 'invoice_date', 'type')
    def _compute_amount_with_discount(self):
        for move in self:
            round_curr = move.currency_id.round
            # discounted here means to be discounted, sorry future devs
            discounted, undiscounted = sum(line.price_total for line in move.invoice_line_ids.filtered(lambda l: not l.exclude_discount)), sum(
                line.price_total for line in move.invoice_line_ids.filtered(lambda l: l.exclude_discount))

            amount_discounted_company, amount_undiscounted_company = discounted, undiscounted
            if move.currency_id and move.company_id and move.currency_id != move.company_id.currency_id:
                currency_id = move.currency_id
                amount_discounted_company = currency_id._convert(
                    discounted, move.company_id.currency_id, move.company_id, move.invoice_date or fields.Date.today())
                amount_undiscounted_company = currency_id._convert(
                    undiscounted, move.company_id.currency_id, move.company_id, move.invoice_date or fields.Date.today())

            sign = move.type in ['in_refund', 'out_refund'] and -1 or 1
            move.amount_discounted_company_signed = amount_discounted_company * sign
            move.amount_undiscounted_company_signed = amount_undiscounted_company * sign
            move.amount_discounted_signed = discounted * sign
            move.amount_undiscounted_signed = undiscounted * sign

    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    exclude_discount = fields.Boolean('Exclude Discount')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        for rec in res:
            # cannot call onchange product id since it will pull the original price for products
            rec.exclude_discount = rec.product_id.exclude_discount
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        vals = super(AccountMoveLine, self)._onchange_product_id()
        self.exclude_discount = self.product_id.exclude_discount  # not using compute so that we only pull this info once
        return vals
