odoo.define('branom_website_partner_delivery.checkout', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');

    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();

    publicWidget.registry.websiteSaleDelivery = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        events: {
            'click .o_delivery_carrier_select': '_onCarrierClick',
        },

        _onCarrierClick: function (ev) {
            var $radio = $(ev.currentTarget).find('input[type="radio"]');
            $radio.prop("checked", true);
            var $payButton = $('#o_payment_form_pay');
            $payButton.prop('disabled', true);
            var is_partner_acct = $radio.data('is_partner_shipping');
            if(!is_partner_acct) {
                is_partner_acct = false;
            }
            dp.add(this._rpc({
                route: '/sale_change_shipping_account',
                params: {
                    carrier_id: $radio.val(),
                    partner_acct: is_partner_acct,
                },
            })).then(function(result) {
                // Enable Button if write is successful
                $payButton.prop('disabled', false);
            });
        },

    });
});