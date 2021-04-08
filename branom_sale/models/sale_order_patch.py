from odoo.addons.website_delivery_ups.models.sale import SaleOrder

def _create_delivery_line(self, carrier, price_unit):
    if self.carrier_id.delivery_type == 'ups' and self.ups_bill_my_account and self.ups_carrier_account:
        self.ups_service_type = carrier.ups_default_service_type
        return super(SaleOrder, self)._create_delivery_line(carrier, 0.0)
    return super(SaleOrder, self)._create_delivery_line(carrier, price_unit)


SaleOrder._create_delivery_line = _create_delivery_line
