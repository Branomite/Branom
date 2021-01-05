odoo.define('gcl_website.payment_terms', function (require) {
    "use strict";

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();

    console.log('v1.00 - RFQ');

    $(document).ready(function () {

        // Add item to quote
        $('#add_to_quote').click(function (ev) {
            ev.preventDefault();
            self = $(this);
            var values = {
                'product_id': self.data('id'),
                'operation': 'create',
            }
            dp.add(ajax.jsonRpc('/shop/product/rfq/update', 'call', values)).then(_addSaleRfqLines);
        });

        // Remove item from quote
        $('.js_delete_rfq_product').click(function () {
            self = $(this);
            var values = {
                'product_id': self.data('product-id'),
                'operation': 'delete',
            }
            dp.add(ajax.jsonRpc('/shop/product/rfq/update', 'call', values)).then(_removeSaleRfqLines);
        });

        // Update item qty to quote
        $('.js_update_rfq_qty').click(function () {
            self = $(this);
            var qty = $('.js_rfq_quantity_input').val();
            var values = {
                'product_id': self.data('product-id'),
                'operation': 'update',
                'request_qty': qty,
            }
            dp.add(ajax.jsonRpc('/shop/product/rfq/update', 'call', values)).then(_updateSaleRfqLines);
        });

        $('.js_rfq_quantity_input').on('change', function(){
            self = $(this);
            var qty = self.val();
            var values = {
                'product_id': self.data('product-id'),
                'operation': 'update',
                'request_qty': qty,
            }
            dp.add(ajax.jsonRpc('/shop/product/rfq/update', 'call', values)).then(_updateSaleRfqLines);
        })

        var _addSaleRfqLines = function() {
            console.log('ADD SALE RFQ CALLED');
            window.location = '/shop';
        }

        var _updateSaleRfqLines = function() {
            console.log('UPDATE SALE RFQ CALLED');
            location.reload();
        }

        var _removeSaleRfqLines = function() {
            console.log('REMOVE SALE RFQ CALLED');
            location.reload();
        }

    }); // DRF

}); // DEFINE
