odoo.define('branom_website_sale.portal_payment', function (require) {
    "use strict";

    require('web.dom_ready');
    // var ajax = require('web.ajax');
    var rpc = require('web.rpc');

    var custom_btn = $('#custom_tx_amount');
    var invoice_btn = $('#invoice_tx_amount');
    var invoice_checkboxes = $('.invoice_line_checkbox');
    var payment_type = $('.portal_payment_type');

    // Handling for Invoice box
    var invoice_container = $('#account_portal_invoices_container');
    // Custom Amount Click
    custom_btn.click(function () {
        var amount = $('#pm_amount');
        invoice_container.addClass('d-none');
        amount.prop('disabled', false);
        amount.val('');
        invoice_checkboxes.prop('checked', false);
    });
    // Pay Invoices Click
    invoice_btn.click(function () {
        var amount = $('#pm_amount');
        invoice_container.removeClass('d-none');
        $('#pm_amount').prop('disabled', true);
        amount.val('');
    });

    // Invoice checkbox clicks
    invoice_checkboxes.click(function () {

        var $sum_total = 0;

        // Add Amount to pm_amount Input for all checked invoices
        var checked_invoices = $('.invoice_line_checkbox:checked');
        checked_invoices.each(function () {
            $sum_total = Number($(this).data('amount')) + $sum_total;
            return $sum_total
        });

        $('#pm_amount').val($sum_total.toFixed(2));

    });

    // Add New Card Click - not needed for auth
    $('#init_pm_add').click(function () {
        $('input[data-info="new_pm"]').click();
        $('#init_pm_add').addClass('d-none');
        $('#o_payment_form_add_pm').removeClass('d-none');
        _onRequiredInputClick();
    });

    // Reset form if new card is selected - not needed for auth
    $('input[name="pm_id"]').click(function () {
        if ($('input[data-info="new_pm"]').is(':checked') != true) {
            $('#init_pm_add').removeClass('d-none');
            $('#o_payment_form_add_pm').addClass('d-none');
        }
    });

    // Check all required inputs and clear submit button
    var _onRequiredInputClick = function (ev) {
        var pm_token = $('input[name="pm_id"][data-is-required="true"]:checked').prop('checked');
        var pm_amount = Number($('#pm_amount').val()) > 0;
        var pm_terms = $('#checkbox_portal_cgv').prop('checked');

        if (pm_token && pm_amount && pm_terms) {
            $('#submit_portal_payment').removeClass('disabled');
        } else {
            $('#submit_portal_payment').addClass('disabled');
        }

    };
    var $required_inputs = $('input[data-is-required="true"]');
    $required_inputs.click(_onRequiredInputClick);
    var $amount_input = $('#pm_amount');
    $amount_input.on('input', _onRequiredInputClick);

    var $process_payment = function() {
        // Find values based on values in buttons container
        var submit_btn = $('#submit_portal_payment');
        var token_id = $('input:checked[name="pm_id"][data-is-required="true"]').val();
        var payment_name = $('input:checked[name="pm_id"][data-is-required="true"]').data('pm-name');
        var amount = $('#pm_amount').val();
        var memo = $('#pm_memo').val();
        var partner_id = $('.o_payment_form').data('partner-id');
        var website_id = $('input[name="website_id"]').val();
        var payment_type = $('.portal_payment_type:checked').data('type');
        var checked_invoices = $('.invoice_line_checkbox:checked');

        var invoice_ids = [];

        checked_invoices.each(function () {
            var this_id = $(this).data('id');
            invoice_ids.push(this_id);
        });

        // Filter out potentially dangerous characters from memo
        var memo_filtered = memo.replace(/[`~!@#$%^&*()_|+=?;:'",<>]/gi, '');

        amount = Number(amount);
        // Send data to get processed
        rpc.query({
            model: 'account.payment',
            method: 'create_account_payment',
            args: [{
                'amount': amount,
                'invoice_ids': invoice_ids,
                'memo': memo_filtered,
                'partner_id': partner_id,
                'payment_type': payment_type,
                'token_id': token_id,
                'payment_name': payment_name,
                'website_id': website_id,
            }],
        }).then(function (result) {
            submit_btn.prop('disabled', false);
            $.unblockUI();
            alert('Your Payment is being processed!');
            window.location = '/my/home';
        }, function (error) {
            console.log(error);
            submit_btn.prop('disabled', false);
            $.unblockUI();
            var message = 'Processing Error';
            if (error['data'] != 'undefined') {
                message += ': ' + error;
            }
            alert(message);
        });
    };

    // Payment Button Submit Action
    $('#submit_portal_payment').click(function (ev) {
        ev.preventDefault();
        var amount = $('#pm_amount').val();
        var partner_id = $('.o_payment_form').data('partner-id');
        var submit_btn = $('#submit_portal_payment');

        // Get Partner Credit Field
        rpc.query({
            model: 'account.payment',
            method: 'get_partner_credit_amount',
            args: [{
                'partner_id': partner_id,
            }],
        }).then(function (result) {

            var overpayment_amount = 0;
            var overpayment = false;
            // Conditions for overpayment
            if(result < 0) {
                overpayment_amount = Number(result) - Number(amount);
                overpayment = true;
            } else {
                overpayment_amount = Number(amount) - Number(result);
                if(overpayment_amount > 0) {
                    overpayment = true;
                }
            }
            // Proceed if there is no overpayment
            if (overpayment === false) {
                submit_btn.prop('disabled', 'disabled');
                $.blockUI();
                $process_payment();
                // Ask to confirm if there is an overpayment
            } else if (confirm(
                'You are about to make a payment of $' +
                amount.toString() +
                ' and there is a balance of $' +
                Math.abs(result).toFixed(2) +
                ' on your account.  Do you wish to make an overpayment of $'
                + Math.abs(overpayment_amount).toFixed(2) + '?')
            ){
                submit_btn.prop('disabled', 'disabled');
                $.blockUI();
                // Process Payment
                $process_payment();
            } else {
                console.log('No payment made');
            }
        });
    });
});
