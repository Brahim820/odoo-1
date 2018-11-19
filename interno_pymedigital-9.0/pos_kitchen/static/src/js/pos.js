odoo.define('pos_kitchen', function(require){
    var pos_sync_order = require('pos_sync_order');
    var session = require('web.session');
    var Backbone = window.Backbone;
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var models = require('point_of_sale.models');
    var bus = require('bus.bus');
    var gui = require('point_of_sale.gui');
    var chrome = require('point_of_sale.chrome')
    var PosPopWidget = require('point_of_sale.popups');
    var QWeb = core.qweb;
    var _t = core._t;


var KitchenScreenWidget = PosBaseWidget.extend({
    template: 'KitchenScreenWidget',

    renderElement: function(){
        var self = this;
        this._super();
    },

    show: function(){
        var self = this;
        this._super();
            var kitchen_data = self.pos.pos_kitchen_data;
            var receipt ="";
            for(var i=0;i<kitchen_data.length;i++){
                receipt += QWeb.render('KitchenReceiptWidget',{widget:self,'data':kitchen_data[i], 'wvid':i});
            }
            if(receipt == ""){
                receipt = "<div class='order-empty' style='color:gainsboro'><i style='font-size: 253px;'class='fa fa-shopping-cart' /><h1>Your Order cart is empty</h1></div>"
            }
            this.$(".kitchen_screen").html(receipt);
            this.$(".button_cooked").click(function(){
                var id = parseInt($(this).attr("data-id"));
                var order_line_id = parseInt($(this).attr("data-orderline_id"))
                kitchen_data[id].lines[order_line_id][2].order_line_status = 1;
                var data = kitchen_data[id]
                self.pos.sync_session.send({'action':'update_order','order':data});
                self.pos.chrome.gui.show_screen('kitchen_screen',{},'refresh');
            });  
            this.$(".button_delivered").click(function(){
                var id = parseInt($(this).attr("data-id"));
                var order_line_id = parseInt($(this).attr("data-orderline_id"))
                var data = kitchen_data[id]
                kitchen_data[id].lines[order_line_id][2].order_line_status = 2;
                self.pos.sync_session.send({'action':'update_order','order':data});
                self.pos.chrome.gui.show_screen('kitchen_screen',{},'refresh');

            });
            this.$(".wv_print").click(function(){
                var id = parseInt($(this).attr("data-id"));
                var data = kitchen_data[id]
                var env = {
                    widget:  self,
                    data: data,
                };
                var receipt = QWeb.render('XmlKitchenReceipt',env);
                self.pos.proxy.print_receipt(receipt);
            });  
        },
        close: function(){  
        },   
        get_product_by_id: function(id){
            return this.pos.db.get_product_by_id(id).display_name;
        },

        get_partner_by_id:function(id){
            return  this.pos.db.get_partner_by_id(id);
        },
    });
    gui.define_screen({
        'name': 'kitchen_screen', 
        'widget': KitchenScreenWidget,
    });
    chrome.Chrome.include({
        build_widgets: function() {
            var self = this;
            this._super();
            if(this.pos.config.pos_kitchen_view){
                setTimeout(function(){ self.gui.show_screen('kitchen_screen'); }, 5); 
            }
        },
    });
    var WVOrderlineNoteButton = screens.ActionButtonWidget.extend({
        template: 'WVOrderlineNoteButton',
        button_click: function(){
            var line = this.pos.get_order().get_selected_orderline();
            if (line) {
                this.gui.show_popup('textarea',{
                    title: _t('Add extra utility note'),
                    value:   line.wvget_note(),
                    confirm: function(note) {
                        line.wvset_note(note);
                        line.trigger('change',this);
                    },
                });
            }
        },
    });

    screens.define_action_button({
        'name': 'wvorderline_note',
        'widget': WVOrderlineNoteButton,
        'condition': function(){
            return true; //this.pos.config.wv_order_line_note;
        },
    });
    

    var PriorityPopupWidget = PosPopWidget.extend({
        template: 'PriorityPopupWidget',

        renderElement: function(){
            this._super(); 
            var self = this;
            $(".change_priorty").click(function(){
                var order = self.pos.get_order();
                order.order_priority = $(".priority_state").val();
                self.pos.sync_session.send({'action':'update_order','order':self.pos.get('selectedOrder').export_as_JSON()});
                self.click_cancel();
            });         
        },
        show: function(options){
            this.options = options || {};
            var self = this;
            this._super(options); 
            this.renderElement();
        },
    });

    gui.define_popup({
        'name': 'priority-popup', 
        'widget': PriorityPopupWidget,
    });

    var WVOrderPriorityeButton = screens.ActionButtonWidget.extend({
        template: 'WVOrderPriorityeButton',
        button_click: function(){
            var order = this.pos.get_order();
            if (order) {
                this.gui.show_popup('priority-popup',{'order_priority':order.order_priority});
            }
        },
    });

    screens.define_action_button({
        'name': 'order_priority',
        'widget': WVOrderPriorityeButton,
        'condition': function(){
            return true;//this.pos.config.wv_allow_order_priority;
        },
    });
    
    var SyncSessionSuper = pos_sync_order.SyncSession;
    pos_sync_order.SyncSession = pos_sync_order.SyncSession.extend({
        send: function(order){
            var self = this;
            openerp.session.rpc("/pos_sync_session/", {
                    session_id: self.pos.config.wv_session_id[0],
                    order: order,
                    pos_config_id:self.pos.config.id,
                }).done(function(results){
                    if(typeof results === "object"){
                        if(results['action']=='sync_all_orders'){
                            if(results['order'].length >0){
                                if(self.pos.config.pos_kitchen_view){
                                _.each(results['order'], function(item) {
                                   self.pos.pos_kitchen_data.push(item['order']);
                                });
                                self.pos.chrome.gui.show_screen('kitchen_screen',{},'refresh');
                                }
                                else{
                                    _.each(results['order'], function(res){
                                    self.pos.update_the_order(res['order']);
                                    });
                                    var uid_list = [];
                                    for(var i=0;i<results['order'].length;i++){
                                        uid_list.push(results['order'][i]['order'].uid);
                                    }
                                    if(uid_list.length > 0){
                                        var list_orders = self.pos.get('orders');
                                        _.each(list_orders.models, function(wvorder){
                                            if(wvorder != undefined){
                                                if(uid_list.indexOf(wvorder.uid)<0){
                                                   wvorder.destroy({'reason': 'abandon'}); 
                                                }
                                            }
                                        });
                                    }
                                }
                            }
                        }
                    }
                    self.allow_remove_sync = true;
                }).fail(function (error, e) {
                    e.preventDefault();
                    console.log("Please Check your Internet Connection.")
                });
        },
        bus_notification: function(bus_messages) {
            self = this;
            if(bus_messages.length > 0){
                var bus_message = bus_messages[0]
                if(bus_message[0][1] == "pos_sync_session"){
                    if(this.pos.config.pos_kitchen_view){
                        if(bus_message[1]['action']=="update_order"){
                            var all_data = this.pos.pos_kitchen_data;
                            var p_tok = true;
                            for(var i=0;i<all_data.length;i++){
                                if(all_data[i].uid == bus_message[1]['order'].uid){
                                    p_tok = false;
                                    this.pos.pos_kitchen_data[i] = bus_message[1]['order'];
                                }
                            }
                            if(p_tok){
                                this.pos.pos_kitchen_data.push(bus_message[1]['order']);
                            }
                            self.pos.chrome.gui.show_screen('kitchen_screen',{},'refresh');
                        }
                        else if(bus_message[1]['action']=="remove_order"){
                            var all_data = this.pos.pos_kitchen_data;
                            for(var i=0;i<all_data.length;i++){
                                if(all_data[i].uid == bus_message[1]['order']){
                                    this.pos.pos_kitchen_data.splice(i, 1);
                                }
                            }
                            self.pos.chrome.gui.show_screen('kitchen_screen',{},'refresh');
                        }
                    }
                    else{
                        if(bus_message[1]['action']=="update_order"){
                            this.pos.update_the_order(bus_message[1]['order']);
                        }
                        else if(bus_message[1]['action']=="remove_order"){
                            var order = this.pos.get('orders').find(function (order) {
                                return order.uid == bus_message[1]['order'];
                            });
                            if(order){
                                order.destroy({'reason': 'abandon'});
                                this.pos.chrome.gui.show_screen(this.pos.chrome.gui.get_current_screen(),{},'refresh');
                            }
                        }

                    }
                    
                }
            }
        },
    });
});
