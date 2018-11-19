odoo.define('pos_restaurant_print_local.print_local', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');

var QWeb = core.qweb;

var multiprint = require('pos_restaurant.multiprint');

if (multiprint.SubmitOrderButton)
{
    var PrintOrderScreenWidget = screens.ReceiptScreenWidget.extend({
        template: 'PrintOrderScreenWidget',
        click_next: function(){
            this.gui.show_screen('products');
        },
        click_back: function(){
            this.gui.show_screen('products');
        },
        render_receipt: function(){

            var printers = this.pos.printers;
            var order = this.pos.get_order();
            for(var i = 0; i < printers.length; i++){
                var changes = order.computeChanges(printers[i].config.product_categories_ids);
                if ( changes['new'].length > 0 || changes['cancelled'].length > 0){

                    this.$('.pos-receipt-container').html(QWeb.render('LocalOrderChangeReceipt',{
                        widget: this,
                        changes: changes,
                    }));
                }
            }
        },
        print_web: function(){
            window.print();
            this.pos.get_order().saveChanges();
        },
    });

    gui.define_screen({name:'print_order', widget: PrintOrderScreenWidget});

    multiprint.SubmitOrderButton.include({
        button_click: function () {

            var order = this.pos.get_order();
            if(order.hasChangesToPrint()) {
                if (this.pos.config.order_print_local) {
                    this.gui.show_screen('print_order');
                    // order.saveChanges(); // AHORA SE ESTAN SALVANDO LOS CAMBIOS CUANDO SE IMPRIMEN (Botón "Print")
                } else {
                    this._super();
                }
            }
        },
    });
}

});
