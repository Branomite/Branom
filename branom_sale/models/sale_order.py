from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sales_type = fields.Selection([
        ('commission', 'Commission Sale'),
        ('regular', 'Non-Commission Sale'),
    ], string="Sales Type")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self.filtered(lambda o: o.state == 'sale' and o.sales_type == 'commission'):
            for line in order.order_line:
                line.qty_delivered_method = 'manual'
                line.qty_delivered = line.product_uom_qty
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
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
                return super(SaleOrderLine, self)._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
        return True

    # deprecated in v13
    # def invoice_line_create_vals(self, invoice_id, qty):
    #     res = super(SaleOrderLine, self).invoice_line_create_vals(invoice_id, qty)
    #     for line in res:
    #         # Take the unit_price and subtract the discount amount, set as new invoice unit price.
    #         line['price_unit'] = line['price_unit'] - (line['price_unit'] * (line['discount'] / 100.0))
    #         line['discount'] = 0.0
    #     return res

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        # Take the unit_price and subtract the discount amount, set as new invoice unit price.
        res['price_unit'] = res['price_unit'] - \
            (res['price_unit'] * (res['discount'] / 100.0))
        res['discount'] = 0.0

    def get_sale_order_line_multiline_description_sale(self, product):
        if not product.attribute_line_ids.value_ids:
            res = super(SaleOrderLine, self).get_sale_order_line_multiline_description_sale(product)
        else:
            if product.code:
                new_description = "[" + product.code + "] " + product.name + "\n"
            else:
                new_description = product.name + "\n"

            for attr_val in product.mapped('product_template_attribute_value_ids.product_attribute_value_id'):
                mc_code = attr_val.manufacture_code or ''
                custom_val = self.product_custom_attribute_value_ids.filtered(lambda c: c.attribute_value_id == attr_val).custom_value

                new_description = new_description + mc_code + ": " + attr_val.attribute_id.name + " - " + attr_val.name
                # Handle custom value in desc
                if custom_val:
                    new_description = new_description + ((": " + custom_val) or '').strip() + "\n"
                else:
                    new_description = new_description + "\n"
            res = new_description
        return res
