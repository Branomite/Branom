odoo.define('branom_website_sale.quick_order', function (require) {
    require('web.dom_ready');
    var ajax = require('web.ajax');
    console.log('Quick Order version 1.0.8');

    function validateForm() {
        // if form valid
        var is_invalid_count = $('input.brnm_sku_input.is-invalid').length;
        var is_valid_count = $('input.brnm_sku_input.is-valid').length;
        if ((is_invalid_count == 0) && (is_valid_count > 0)) {
            $('.brnm_qo_add_to_cart').prop('disabled', false);
        } else {
            $('.brnm_qo_add_to_cart').prop('disabled', 'disabled');
        }
    };

    // sku_input should be an input control or a jquery object containing one input control
    function bindSKUValidation(sku_input) {
        var sku_input = $(sku_input);

        sku_input.on('focusout', function (e) {
            $(e.currentTarget).val(function (index, value) {
                return value.trim();
            });
            var sku = $(e.currentTarget).val();
            //console.log('sku:', sku);
            if (sku) {
                var data = {'sku': sku};
                //console.log(data);
                ajax.jsonRpc('/quick-order/validate', 'call', data).then(function (result) {
                    var validation_msg = sku_input.next('.brnm_qo_feedback');
                    if (result.success) {
                        //row.attr('sku_validated', true);
                        sku_input.removeClass('is-invalid').addClass('is-valid');
                        validation_msg.removeClass('invalid-feedback').addClass('valid-feedback');
                        validation_msg.text(result.message);
                    } else {
                        //row.attr('sku_validated', false);
                        sku_input.removeClass('is-valid').addClass('is-invalid');
                        validation_msg.removeClass('valid-feedback').addClass('invalid-feedback');
                        validation_msg.text('Product not found.');
                    }
                    validateForm();
                });
            } else {
                //row.removeAttr('sku_validated');
                sku_input.removeClass('is-valid is-invalid');
                validateForm();
            }
        });
    };
    // run on page load
    $('input.brnm_sku_input').each(function (index, sku_input) {
        bindSKUValidation(sku_input);
    });

    // add new row
    function addRowCallback(e) {
        //console.log('Adding row');

        var row = $('.quick_order_row:last').clone();
        var line_num = row.data('lineNum') + 1;
        row.attr('data-line-num', line_num);
        row.find('input').each(function (index, el) {
            var $el = $(el);
            if ($el.hasClass('brnm_sku_input')) {
                $el.val('');
                $el.attr('name', 'item_num_' + line_num);
                bindSKUValidation($el);
            } else {
                $el.val('1');
                $el.attr('name', 'item_qty_' + line_num);
            }
        });
        row.appendTo('.quick_order_lines');
    }

    $('.brnm_qo_add_item').on('click', addRowCallback);

    function formSubmitCallback(e) {
        e.preventDefault();
        $('.brnm_qo_add_to_cart').prop('disabled', true);
        console.log('brnm_quickorder_form submitted');
        var form_data = $(this).serializeArray();
        //console.log(form_data);
        var products = [];
        var product = {};
        form_data.forEach(function (item, index, array) {
            if (item['name'].includes('item_num')) {
                product.sku = item['value'];
            } else if (item['name'].includes('qty')) {
                product.qty = item['value'];
                if (product.sku && product.qty > 0) {
                    products.push(product);
                }
                product = {};
            }
        });

        console.log(products);

        ajax.jsonRpc('/quick-order/add-items', 'call', {'products': products}).then(function (result) {
            if (result.success) {
                window.location.replace('/shop/cart');
            } else {
                // display errors
                if ('errors' in result) {
                    var alert = $('.brnm_qo_errors');
                    var err_list = alert.find('ul');
                    err_list.empty();
                    result.errors.forEach(function (err) {
                        console.warn(err);
                        var li = document.createElement('li');
                        li.innerHTML = err;
                        err_list.append(li);
                        alert.show();
                    });
                }
            }
        });
    }

    $('.brnm_quickorder_form').on('submit', formSubmitCallback);

    return {
        bindSKUValidation: bindSKUValidation,
        addRowCallback: addRowCallback,
        formSubmitCallback: formSubmitCallback
    };
});