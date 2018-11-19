odoo.define('l10n_ec_pos_sri.screens', function (require) {
"use strict";

var PosScreens = require('point_of_sale.screens');
var core = require('web.core');
var Model = require('web.DataModel');
var _t = core._t;

    /* Save edited fields or created data into res_partner */
    PosScreens.ClientListScreenWidget.include({

        save_client_details: function(partner) {
            var self = this;

            var fields = {};
            this.$('.client-details-contents .detail').each(function(idx,el){
                fields[el.name] = el.value;
            });

            if (!fields.name) {
                this.gui.show_popup('error',_t('A Customer Name Is Required'));
                return;
            }

            if (this.uploaded_picture) {
                fields.image = this.uploaded_picture;
            }

            fields.id           = partner.id || false;
            fields.country_id   = fields.country_id || false;
            fields.barcode      = fields.barcode || '';

            // begin ec
            // TODO: get fiscal position and use those default accounts for payment.
            // fields.property_account_position_id   = fields.property_account_position_id || false;

            if (fields.vat) {
                var country_code = fields.vat.substring(0, 2);
                if (!isNaN(country_code)) {
                    var code = 'EC'; // TODO: upper country's code or 'EC'
                    fields.vat = String(code) + String(fields.vat);
                }

            }
            // end ec

            new Model('res.partner').call('create_from_ui',[fields]).then(function(partner_id){
                self.saved_client_details(partner_id);
            },function(err,event){
                event.preventDefault();
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': _t('Your Internet connection is probably down.'),
                });
            });
        },

    });


    PosScreens.PaymentScreenWidget.include({

        validate_order: function(force_validation) {
            var self = this;

            var order = self.pos.get_order();
            if (order){
                order.establecer_secuencial(this.pos.get_sequential());
            }

            this._super(force_validation);

            if (order){
                this.pos.get_next_sequential();
            }
        },
    });

});