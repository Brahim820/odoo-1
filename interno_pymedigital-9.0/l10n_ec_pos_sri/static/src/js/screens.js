odoo.define('l10n_ec_pos_sri.screens', function (require) {
"use strict";

var PosScreens = require('point_of_sale.screens');
var core = require('web.core');
var Model = require('web.DataModel');
var _t = core._t;

PosScreens.ScreenWidget.include({
    // this method shows the screen and sets up all the widget related to this screen. Extend this method
    // if you want to alter the behavior of the screen.
    show: function(){
        var self = this;

        this.hidden = false;
        if(this.$el){
            this.$el.removeClass('oe_hidden');
        }

        this.pos.barcode_reader.set_action_callback({
            'cashier': _.bind(self.barcode_cashier_action, self),
            'product': _.bind(self.barcode_product_action, self),
            'client' : _.bind(self.barcode_client_action, self),
            'discount': _.bind(self.barcode_discount_action, self),
            'error'   : _.bind(self.barcode_error_action, self),
        });
    }
});

/* Save edited fields or created data into res_partner */
PosScreens.ClientListScreenWidget.include({
    barcode_client_action: function(code){
        if (this.editing_client) {
            this.$('.detail.barcode').val(code.code);
        } else if (this.pos.db.get_partner_by_barcode(code.code)) {
            this.display_client_details('show',this.pos.db.get_partner_by_barcode(code.code));
        }
    },

    // what happens when we save the changes on the client edit form -> we fetch the fields, sanitize them,
    // send them to the backend for update, and call saved_client_details() when the server tells us the
    // save was successfull.
    save_client_details: function(partner) {
        var self = this;
        
        var fields = {};
        this.$('.client-details-contents .detail').each(function(idx,el){
            fields[el.name] = el.value;
        });

        if (!fields.name) {
            this.gui.show_popup('error',_t('El nombre del cliente es obligatorio.'));
            return;
        }
        
        if (this.uploaded_picture) {
            fields.image = this.uploaded_picture;
        }

        fields.id           = partner.id || false;
        fields.country_id   = fields.country_id || false;
        fields.property_account_position_id   = fields.property_account_position_id || false;
        fields.barcode      = fields.barcode || '';
        fields.vat   = fields.vat || false;
        if (fields.vat) {
            fields.vat = 'EC' + String(fields.vat)
        }
        
        if($(".Validar-la-identificación").is(':checked')) 
            fields.do_check_vat = 1;
        else
            fields.do_check_vat = 0;
        
        fields.state_id   = fields.state_id || false;
        var property_account_position_id = fields.property_account_position_id 
        var vat = fields.vat
        // if(property_account_position_id !== false){
        //     if(vat !== false){
        //         new Model('res.partner').call('check_vat_from_ui',[property_account_position_id, vat]).then(function(error_title){
        //             self.gui.show_popup('error',{
        //             'title': _t('Error: Could not Save Changes'),
        //             'body': _t(error_title),

        //             });
        //         });
        //         return;
        //     }
        // }
        new Model('res.partner').call('create_from_ui',[fields]).then(function(partner_id){
            self.saved_client_details(partner_id);
        },function(err,event){
            event.preventDefault();
            self.gui.show_popup('error',{
                'title': _t('Error: Could not Save Changes'),
                'body': _t('Ya existe un cliente con la C.I o R.U.C. ingresado.'),
             
            });
        });
    },
});

PosScreens.PaymentScreenWidget.include({
    // Check if the order is paid, then sends it to the backend,
    // and complete the sale process
    validate_order: function(force_validation) {
        var self = this;

        var order = this.pos.get_order();

        // FIXME: this check is there because the backend is unable to
        // process empty orders. This is not the right place to fix it.
        if (order.get_orderlines().length === 0) {
            this.gui.show_popup('error',{
                'title': _t('Empty Order'),
                'body':  _t('There must be at least one product in your order before it can be validated'),
            });
            return;
        }

        // get rid of payment lines with an amount of 0, because
        // since accounting v9 we cannot have bank statement lines
        // with an amount of 0
        order.clean_empty_paymentlines();

        var plines = order.get_paymentlines();
        for (var i = 0; i < plines.length; i++) {
            if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                this.pos_widget.screen_selector.show_popup('error',{
                    'message': _t('Negative Bank Payment'),
                    'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                });
                return;
            }
        }

        if (!order.is_paid() || this.invoicing) {
            return;
        }

        // The exact amount must be paid if there is no cash payment method defined.
        if (Math.abs(order.get_total_with_tax() - order.get_total_paid()) > 0.00001) {
            var cash = false;
            for (var i = 0; i < this.pos.cashregisters.length; i++) {
                cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
            }
            if (!cash) {
                this.gui.show_popup('error',{
                    title: _t('Cannot return change without a cash payment method'),
                    body:  _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                });
                return;
            }
        }

        // if the change is too large, it's probably an input error, make the user confirm.
        if (!force_validation && (order.get_total_with_tax() * 1000 < order.get_total_paid())) {
            this.gui.show_popup('confirm',{
                title: _t('Please Confirm Large Amount'),
                body:  _t('Are you sure that the customer wants to  pay') + 
                       ' ' + 
                       this.format_currency(order.get_total_paid()) +
                       ' ' +
                       _t('for an order of') +
                       ' ' +
                       this.format_currency(order.get_total_with_tax()) +
                       ' ' +
                       _t('? Clicking "Confirm" will validate the payment.'),
                confirm: function() {
                    self.validate_order('confirm');
                },
            });
            return;
        }

        if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) { 

                this.pos.proxy.open_cashbox();
        }

        if (order.is_to_invoice()) {
            var invoiced = this.pos.push_and_invoice_order(order);
            this.invoicing = true;

            invoiced.fail(function(error){
                self.invoicing = false;
                if (error.message === 'Missing Customer') {
                    self.gui.show_popup('confirm',{
                        'title': _t('Please select the Customer'),
                        'body': _t('You need to select the customer before you can invoice an order.'),
                        confirm: function(){
                            self.gui.show_screen('clientlist');
                        },
                    });
                } else if (error.code < 0) {        // XmlHttpRequest Errors
                    self.gui.show_popup('error',{
                        'title': _t('The order could not be sent'),
                        'body': _t('Check your internet connection and try again.'),
                    });
                } else if (error.code === 200) {    // OpenERP Server Errors
                    self.gui.show_popup('error-traceback',{
                        'title': error.data.message || _t("Server Error"),
                        'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                    });
                } else {                            // ???
                    self.gui.show_popup('error',{
                        'title': _t("Unknown Error"),
                        'body':  _t("The order could not be sent to the server due to an unknown error"),
                    });
                }
            });

            invoiced.done(function(){
                self.invoicing = false;
                order.finalize();
            });
        } else {
            this.pos.push_order(order);
            this.gui.show_screen('receipt');
        }
    },
})

});
