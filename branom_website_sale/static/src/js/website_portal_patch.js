odoo.define('gcl_website_sale.website_portal', function () {
    "use strict";

    $(document).ready(function(){

        // Went this route because I couldn't get the t-att-href="/my/credit/{{payment.id}} to work in xml
        $('.payment_line_id').click(function(){
            var self = $(this);
            var id = self.data('payment-id');
            window.location = '/my/payment/' + id.toString();
        });
    });
});
