# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sales_type = fields.Selection([
        ('commission', 'Commission Sale'),
        ('regular', 'Non-Commission Sale'),
        ], string="Sales Type")

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self.filtered(lambda o: o.state == 'sale' and o.sales_type == 'commission'):
            for line in order.order_line:
                line.qty_delivered_method = 'manual'
                line.qty_delivered = line.product_uom_qty
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_launch_stock_rule(self):
        for line in self:
            if line.order_id.sales_type == 'commission':
                # Still need to create group_id in case it is used elsewhere
                # Following code copied from sale_stock's sale_order.py
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
                line.qty_delivered = line.product_uom_qty
            else:
                return super(SaleOrderLine, self)._action_launch_stock_rule()
        return True

    @api.multi
    def invoice_line_create_vals(self, invoice_id, qty):
        res = super(SaleOrderLine, self).invoice_line_create_vals(invoice_id, qty)
        for line in res:
            # Take the unit_price and subtract the discount amount, set as new invoice unit price.
            line['price_unit'] = line['price_unit'] - (line['price_unit'] * (line['discount']/100.0))
            line['discount'] = 0.0
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        for line in res:
            prod_id = line.product_id
            new_description = "[" + prod_id.code + "] " + prod_id.name + "\n"
            for attr_val in prod_id.attribute_value_ids:
                new_description = new_description + attr_val.manufacture_code + ": " \
                                  + attr_val.attribute_id.name + " - " + attr_val.name + "\n"
        res.name = new_description
        return res
