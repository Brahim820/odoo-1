odoo.define('pos_sync_restaurant', function(require){
    var module = require('point_of_sale.models');
    var models = module.PosModel.prototype.models;

    for(var i=0; i<models.length; i++){
        var model=models[i];
        if(model.model === 'restaurant.floor'){
            model.domain = function(self)
            { 
                return [['pos_config_id','in',self.config.id]];
            }
        }
    }
    var PosModelSuper = module.PosModel;
    module.PosModel = module.PosModel.extend({

        update_the_order: function(sync_order){
            var self = this;
            var order = PosModelSuper.prototype.update_the_order.apply(this, arguments);
            if (sync_order.table_id) {
                order.table = self.tables_by_id[sync_order.table_id];
                order.customer_count = sync_order.customer_count;
                this.gui.screen_instances['floors'].replace();
                this.gui.screen_instances.products.action_buttons.guests.renderElement();
            }
            return order;
        },
    });
    var OrderSuper = module.Order;
    module.Order = module.Order.extend({
        set_customer_count: function (count) {
            var self = this;
            OrderSuper.prototype.set_customer_count.apply(this, arguments);
            setTimeout(function(){
                self.pos.sync_session.send({'action':'update_order','order':self.export_as_JSON()});
            }, 500);
            
        },
    });
});
