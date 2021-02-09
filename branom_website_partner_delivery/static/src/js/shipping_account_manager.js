odoo.define('branom_website_partner_delivery.shipping_account_manager', function (require) {
    "use strict";

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();
    var rpc = require('web.rpc');

    var modal_manager = $('#modal_shipping_account_manager');

    $(document).ready(function () {

        console.log('SHIPPING ACCOUNT MANAGER v1.01');

        // Proc Modal to edit record
        $('.shipping_account_update_btn').click(function (ev) {
            self = $(this);
            // Modal for Record edit/create
            rpc.query({
                model: 'res.partner',
                method: 'render_shipping_account_modal',
                args: [{
                    'partner_id': self.data('partner_id'),
                    'operation': self.data('operation'),
                    'record_id': self.data('record_id'),
                }],
            }).then(function (result) {
                if (result) {
                    $('#shipping_form_placeholder').html(result)
                    $('#modal-operation').html(self.data('operation'))
                    modal_manager.modal();
                }
            });

        });

        // AJAX DATA TO CONTROLLER FROM MODAL
        $('#modal_shipping_account_form').submit(function (ev) {
            ev.preventDefault();
            let self = $(this);
            let data = self.serializeArray();
            // Make array pretty
            var query = {};
            data.forEach(function (i) {
                query[i.name] = i.value;
            });

            dp.add(ajax.jsonRpc('/my/account/delivery/method_update', 'call', query)).then(function (res) {
                if (res['status'] === 'complete') {
                    location.reload();
                } else {
                    alert('Error!');
                }
            });
        });

        // UPDATE SHIPPING ACCOUNT ON SESSION SALE ORDER WHEN SELECTED


    }); // DRF
}); // Odoo