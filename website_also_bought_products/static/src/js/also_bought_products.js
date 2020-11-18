
 /* Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('website_also_bought_products.product_page_bought_view', function (require) {
"use strict";
$(document).ready(function()
{
    // var base = require('web_editor.base');
    var ajax = require('web.ajax');
    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;
        $('.ab-item').on('click', 'a.sub-qty', function (ev) {
            ev.preventDefault();
            var $input = $(this).parent().find("input");
            var val = $input.val();
            val = parseFloat(val) - 1;
            if (val <= 1)
            val = 1
            $input.val(val)
        });
        $('.ab-item').on('click', 'a.add-qty', function (ev) {
            ev.preventDefault();
            var $input = $(this).parent().find("input");
            var val = $input.val();
            val = parseFloat(val) + 1;
            if (val <= 1)
            val = 1
            $input.val(val)
        });
        $('.ab-item .add-to-cart').on('click', function (ev){
            var product_id = $(this).attr("product-id");
            var qty = $(this).parent().find("input").val();
            ajax.jsonRpc("/also/bought/add_to_cart", 'call', {'product_id': product_id,'qty':qty}).then(function(data)
            {
                location.pathname="/shop/cart";
            });
        });

    });
});
});
