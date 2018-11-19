odoo.define('pos_keyboard.pos', function (require) {
    "use strict";

    var core = require('web.core');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var PosDB = require("point_of_sale.DB");

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            this.keypad = new Keypad({'pos': this});
            return _super_posmodel.initialize.call(this, session, attributes);
        },
        load_orders: function(){
            var self =this;
            var jsons = this.db.get_unpaid_orders();
            var orders = [];
            var not_loaded_count = 0;
            
            for (var i = 0; i < jsons.length; i++) {
                var json = jsons[i];
                for (var j = 0; j < json.lines.length; j++){
                    var line = json.lines[j];
                    var product = this.db.get_product_by_id(line[2].product_id);
                    if(!product){
                        this.db.remove_unpaid_order(json)
                    }
                }
            }
            
            var jsons_unpaid_orders = this.db.get_unpaid_orders();
            
            for (var i = 0; i < jsons_unpaid_orders.length; i++) {
                var json = jsons_unpaid_orders[i];
                if (json.pos_session_id === this.pos_session.id) {
                    orders.push(new models.Order({},{
                        pos:  this,
                        json: json,
                    }));
               } else {
                    not_loaded_count += 1;
               }
            }

            if (not_loaded_count) {
                console.info('There are '+not_loaded_count+' locally saved unpaid orders belonging to another session');
            }
            
            orders = orders.sort(function(a,b){
                return a.sequence_number - b.sequence_number;
            });
            if (orders.length) {
                this.get('orders').add(orders);
            }
        },
    });

    models.load_fields("product.product",['pos_code']);

    screens.NumpadWidget.include({
        start: function() {
            this._super();
            var self = this;
            this.pos.keypad.set_action_callback(function(data){
                 self.keypad_action(data, self.pos.keypad.type);
            });
        },
        keypad_action: function(data, type){
             if (data.type === type.numchar){
                 this.state.appendNewChar(data.val);
             }
             else if (data.type === type.bmode) {
                 this.state.changeMode(data.val);
             }
             else if (data.type === type.sign){
                 this.clickSwitchSign();
             }
             else if (data.type === type.backspace){
                 this.clickDeleteLastChar();
             }
        }
    });
    
    screens.PaymentScreenWidget.include({
        show: function(){
            this._super();
            this.pos.keypad.disconnect();
        },
        hide: function(){
            this._super();
            this.pos.keypad.connect();
        }
    });
    
    // this module mimics a keypad-only cash register. Use connect() and 
    // disconnect() to activate and deactivate it.
    var Keypad = core.Class.extend({
        init: function(attributes){
            this.pos = attributes.pos;
            /*this.pos_widget = this.pos.pos_widget;*/
            this.type = {
                numchar: 'number, dot',
                bmode: 'quantity, discount, price',
                sign: '+, -',
                backspace: 'backspace'
            };
            this.data = {
                type: undefined,
                val: undefined
            };
            this.action_callback = undefined;
        },

        save_callback: function(){
            this.saved_callback_stack.push(this.action_callback);
        },

        restore_callback: function(){
            if (this.saved_callback_stack.length > 0) {
                this.action_callback = this.saved_callback_stack.pop();
            }
        },

        set_action_callback: function(callback){
            this.action_callback = callback;
        },

        //remove action callback
        reset_action_callback: function(){
            this.action_callback = undefined;
        },

        // starts catching keyboard events and tries to interpret keystrokes,
        // calling the callback when needed.
        connect: function(){
            var self = this;
            // --- additional keyboard ---//
            var KC_PLU = 107;      // KeyCode: + or - (Keypad '+')
            var KC_QTY = 111;      // KeyCode: Quantity (Keypad '/')
            var KC_AMT = 106;      // KeyCode: Price (Keypad '*')
            var KC_DISC = 109;     // KeyCode: Discount Percentage [0..100] (Keypad '-')
            // --- basic keyboard --- //
            var KC_PLU_1 = 83;    // KeyCode: sign + or - (Keypad 's')
            var KC_QTY_1 = 81;     // KeyCode: Quantity (Keypad 'q')
            var KC_AMT_1 = 80;     // KeyCode: Price (Keypad 'p')
            var KC_DISC_1 = 68;    // KeyCode: Discount Percentage [0..100] (Keypad 'd')

            var KC_BACKSPACE = 8;  // KeyCode: Backspace (Keypad 'backspace')       
            var kc_lookup = {
                48: '0', 49: '1', 50: '2',  51: '3', 52: '4',
                53: '5', 54: '6', 55: '7', 56: '8', 57: '9',
                80: 'p', 83: 's', 68: 'd', 190: '.', 81: 'q',
                96: '0', 97: '1', 98: '2',  99: '3', 100: '4',
                101: '5', 102: '6', 103: '7', 104: '8', 105: '9',
                106: '*', 107: '+', 109: '-', 110: '.', 111: '/'
            };

            //usb keyboard keyup event
            var rx = /INPUT|SELECT|TEXTAREA/i;
            var ok = false;
            var timeStamp = 0;
            $('body').on('keyup', '', function (e){
                var statusHandler  =  !rx.test(e.target.tagName)  ||
                    e.target.disabled || e.target.readOnly;
                if (statusHandler){
                    var is_number = false;
                    var type = self.type;
                    var buttonMode = {
                        qty: 'quantity',
                        disc: 'discount',
                        price: 'price'
                    };
                    var token = e.keyCode;
                    if ((token >= 96 && token <= 105 || token == 110) ||
                        (token >= 48 && token <= 57 || token == 190)) {
                        self.data.type = type.numchar;
                        self.data.val = kc_lookup[token];
                        is_number = true;
                        ok = true;
                    }
                    else if (token == KC_PLU || token == KC_PLU_1) {
                        self.data.type = type.sign;
                        ok = true;
                    }
                    else if (token == KC_QTY || token == KC_QTY_1) {
                        self.data.type = type.bmode;
                        self.data.val = buttonMode.qty;
                        ok = true;
                    }
                    else if (token == KC_AMT || token == KC_AMT_1) {
                        self.data.type = type.bmode;
                        self.data.val = buttonMode.price;
                        ok = true;
                    }
                    else if (token == KC_DISC || token == KC_DISC_1) {
                        self.data.type = type.bmode;
                        self.data.val = buttonMode.disc;
                        ok = true;
                    }
                    else if (token == KC_BACKSPACE) {
                        self.data.type = type.backspace;
                        ok = true;
                    } 
                    else {
                        self.data.type = undefined;
                        self.data.val = undefined;
                        ok = false;
                    } 

                    if (is_number) {
                        if (timeStamp + 50 > new Date().getTime()) {
                            ok = false;
                        }
                    }

                    timeStamp = new Date().getTime();

                    setTimeout(function(){
                        if (ok) {self.action_callback(self.data);}
                    }, 50);
                }
            });
        },

        // stops catching keyboard events 
        disconnect: function(){
            $('body').off('keyup', '');
        }
    });

    PosDB.include({
        init: function(options){
            this._super(options);
            this.product_by_code = {};
            this.product_by_pos_code = {};
        },
        add_products: function(products){
            var stored_categories = this.product_by_category_id;

            if(!products instanceof Array){
                products = [products];
            }
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                var search_string = this._product_search_string(product);
                var categ_id = product.pos_categ_id ? product.pos_categ_id[0] : this.root_category_id;
                product.product_tmpl_id = product.product_tmpl_id[0];
                if(!stored_categories[categ_id]){
                    stored_categories[categ_id] = [];
                }
                stored_categories[categ_id].push(product.id);

                if(this.category_search_string[categ_id] === undefined){
                    this.category_search_string[categ_id] = '';
                }
                this.category_search_string[categ_id] += search_string;

                var ancestors = this.get_category_ancestors_ids(categ_id) || [];

                for(var j = 0, jlen = ancestors.length; j < jlen; j++){
                    var ancestor = ancestors[j];
                    if(! stored_categories[ancestor]){
                        stored_categories[ancestor] = [];
                    }
                    stored_categories[ancestor].push(product.id);

                    if( this.category_search_string[ancestor] === undefined){
                        this.category_search_string[ancestor] = '';
                    }
                    this.category_search_string[ancestor] += search_string; 
                    
                }
                this.product_by_id[product.id] = product;
                if(product.barcode){
                    this.product_by_barcode[product.barcode] = product;
                }
                if(product.default_code){
                    this.product_by_code[product.default_code] = product;
                }
                if(product.pos_code){
                    this.product_by_pos_code[product.pos_code] = product;
                }
            }
        },
        get_product_by_code : function(code){
            if(this.product_by_code[code]){
                return this.product_by_code[code];
            }
            return false;
        },
        get_product_by_pos_code : function(pos_code){
            if(this.product_by_pos_code[pos_code]){
                return this.product_by_pos_code[pos_code];
            }
            return false;
        }
    });

    var QuickAddOrderlineWidget = PosBaseWidget.extend({
        template: 'QuickAddOrderlineWidget',
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.ok').click(function(){
                var input_product_code_qty_experession = self.$("#input_product_code_qty_experession").val();
                var order = self.pos.get_order();
                if(input_product_code_qty_experession && input_product_code_qty_experession.length > 0 && 
                        input_product_code_qty_experession.split('*')[0]){
                    var qty = input_product_code_qty_experession.split('*')[1];
                    var code = input_product_code_qty_experession.split('*')[0];
                    if(qty){
                        var product = self.pos.db.get_product_by_code(code);
                        if(product){
                            if($.isNumeric(qty)){
                                order.add_product(product, {quantity: qty });
                                self.$("#input_product_code_qty_experession").val("");
                            }
                        }else{
                            var pos_product = self.pos.db.get_product_by_pos_code(code);
                            if(pos_product){
                                if($.isNumeric(qty)){
                                    order.add_product(pos_product, {quantity: qty });
                                    self.$("#input_product_code_qty_experession").val("");
                                }
                            }
                        }
                    }
                 }
            });
        }
    });

    screens.ProductScreenWidget.include({
        start: function(){ 
            this._super();
            var self = this;
            this.quick_add_orderline_action = new QuickAddOrderlineWidget(this,{});
            this.quick_add_orderline_action.replace(this.$('.placeholder-quick-add-orderline-panel'));
            $("#input_product_code_qty_experession").focus();
        },
        show: function(options){
            options = options || {};
            var self = this;
            this._super();
            $("#input_product_code_qty_experession").focus();
            self.hotkey_handler = function(event){
                if(event.which === 13){
                    self.$('.ok').click()
                }
            };
            $('body').on('keyup',self.hotkey_handler);
        },
        close:function(){
            this._super();
            $('body').off('keyup',this.hotkey_handler);
        },
    });

    return {
        Keypad: Keypad,
        QuickAddOrderlineWidget: QuickAddOrderlineWidget
    };
});
