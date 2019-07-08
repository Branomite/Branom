# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sales_type = fields.Selection([
        ('commission', 'Commission Type'),
        ('regular', 'Temp Regular Type'),
        ], string="Sales Type")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_launch_stock_rule(self):
        for line in self:
            if line.order_id.sales_type == 'commission':
                # Still need to create group_id in case it is used else where
                group_id = line.order_id.procurement_group_id
                if not group_id:
                    group_id = self.env['procurement.group'].create({
                        'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                        'sale_id': line.order_id.id,
                        'partner_id': line.order_id.partner_shipping_id.id,
                    })
                    line.order_id.procurement_group_id = group_id
                else:
                    # In case the procurement group is already created and the order was
                    # cancelled, we need to update certain values of the group.
                    updated_vals = {}
                    if group_id.partner_id != line.order_id.partner_shipping_id:
                        updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                    if group_id.move_type != line.order_id.picking_policy:
                        updated_vals.update({'move_type': line.order_id.picking_policy})
                    if updated_vals:
                        group_id.write(updated_vals)
                # Update the qty delivered to be same as ordered to trigger invoice creation
                # This does not seem like a good idea... If they change the SOL then it does not update
                line.qty_delivered = line.product_uom_qty
            else:
                return super(SaleOrderLine, self)._action_launch_stock_rule()
        return True

    @api.multi
    def invoice_line_create_vals(self, invoice_id, qty):
        res = super(SaleOrderLine, self).invoice_line_create_vals(invoice_id, qty)
        for line in res:
            # Take the unit_price and subtract the discount amount.
            # This will become the new unit price in the invoice.
            # Also reset the discount to 0.0
            line['price_unit'] = line['price_unit'] - (line['price_unit'] * (line['discount']/100))
            line['discount'] = 0.0
        return res

    # @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    # def _onchange_discount(self):
    #     # print("hello")
    #     super(SaleOrderLine, self)._onchange_discount()
    #     # print("did discount change?")
