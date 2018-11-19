odoo.define('pos_validate_client.pos_client', function (require) {
"use strict";
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;

    var _super_order = screens.PaymentScreenWidget.prototype;
    screens.PaymentScreenWidget.include({
        raise_employee_required_error : function(){
            var self = this;
            self.gui.show_popup('error',{
            'title': _t('Cliente no seleccionado.'),
            'body': _t('Seleccione un cliente o consumidor final.'),
            });
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.next').unbind();

            this.$('.next').click(function(){
                if(self.pos.config.is_customer_mandatory){
                    if(self.pos.get_client()) {
                        self.validate_order();
                    }
                    else{
                        self.raise_employee_required_error()
                        return;
                    }
                }
                else{
                   self.validate_order();
                }
            });
        },
    });
});