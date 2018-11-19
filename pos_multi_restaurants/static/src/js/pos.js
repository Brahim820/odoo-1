odoo.define('pos_multi_restaurants.pos_multi_restaurants', function (require) {
"use strict";

	var module = require('point_of_sale.models');
    var models = module.PosModel.prototype.models;

    for(var i=0; i<models.length; i++){
        var model=models[i];
        if(model.model === 'product.product'){
            model.domain = function(self)
            { 
            	if(self.config.pos_multi_restaurant){
            		return [['sale_ok','=',true],['available_in_pos','=',true],['wv_restaurant_id','in',[self.config.pos_multi_restaurant[0]]]]
            	}
            	else{
            		return [['sale_ok','=',true],['available_in_pos','=',true]]
            	}
            }
        } 
        if(model.model === 'restaurant.floor'){
            model.domain = function(self)
            { 
                if(self.config.pos_multi_restaurant){
                    return [['pos_restaurant_id','=',self.config.pos_multi_restaurant[0]]]
                }
                else{
                    return [['pos_config_id','=',self.config.id]];
                }
            }
        }
    }

});
