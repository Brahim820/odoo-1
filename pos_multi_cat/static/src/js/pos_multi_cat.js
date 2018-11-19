odoo.define('pos_multi_cat.pos_multi_cat', function (require) {
"use strict";
var PosDB = require('point_of_sale.DB');

var PosDB = PosDB.include({

	add_products: function(products){
        var stored_categories = this.product_by_category_id;
        if(!products instanceof Array){
            products = [products];
        }
        for(var i = 0, len = products.length; i < len; i++){
            var product = products[i];
            product.product_tmpl_id = product.product_tmpl_id[0];
            var k=0,product_cat_len=(product.pos_categ_id).length;
            do {
            var search_string = this._product_search_string(product);
            var categ_id = product.pos_categ_id ? product.pos_categ_id[k] : this.root_category_id;
            // product.product_tmpl_id = product.product_tmpl_id[0];
            if(product.pos_categ_id=="")
            {
               categ_id=this.root_category_id;
            }
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
            k++;
        }while(k<=product_cat_len);
        }
        },    
    });  
});
