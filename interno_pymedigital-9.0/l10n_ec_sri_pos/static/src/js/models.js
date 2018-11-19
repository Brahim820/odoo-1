odoo.define('l10n_ec_pos_sri.models', function (require) {
"use strict";

var PosModels = require('point_of_sale.models');
var Model = require('web.Model');

/* Load required fields into res_partner */
PosModels.load_fields("res.partner",['property_account_position_id'])

/* ********************************************************
Updating point_of_sale.PosModel
******************************************************** */
var _super_posmodel = PosModels.PosModel.prototype;
PosModels.PosModel = PosModels.PosModel.extend({
    set_establishment: function(value, callback) {
        var self = this;
        if (self.config) {
            self.guardar_configuracion_en_bd('establecimiento', value, function () {
                self.config.establecimiento = value;
                self.asignar_campo_a_orden('establishment', value);
                if (callback){
                    callback();
                }
            });
        }
    },
    get_establishment: function() {
        var establishment = this.config && this.config.establecimiento || 0;
        return establishment || 0;
    },
    set_tipoemision: function(value, callback) {
        var self = this;
        if (self.config) {
            self.guardar_configuracion_en_bd('tipoemision', value, function () {
                self.config.tipoemision = value;
                self.asignar_campo_a_orden('tipoemision', value);
                if (callback){
                    callback();
                }
            });
        }
    },
    get_tipoemision: function() {
        var tipoemision = this.config && this.config.tipoemision || 'F';
        return tipoemision || 'F';
    },
    set_emission_point: function(value, callback) {
        var self = this;
        if (self.config) {
            self.guardar_configuracion_en_bd('puntoemision', value, function () {
                self.config.puntoemision = value;
                self.asignar_campo_a_orden('emission_point', value);
                if (callback){
                    callback();
                }
            });
        }
    },
    get_emission_point: function() {
        var emission_point = this.config && this.config.puntoemision || 0;
        return emission_point || 0;
    },
    set_authorization: function(value, callback) {
        var self = this;
        if (self.config) {
            self.guardar_configuracion_en_bd('autorizacion', value, function () {
                self.config.autorizacion = value;
                self.asignar_campo_a_orden('authorization', value);
                if (callback){
                    callback();
                }
            });
        }
    },
    get_authorization: function() {
        var authorization = this.config && this.config.autorizacion || 0;
        return authorization || 0;
    },
    set_sequential: function(value, callback) {
        var self = this;
        if (self.config) {
            self.guardar_configuracion_en_bd('secuencial', value, function () {
                self.config.secuencial = value;
                self.asignar_campo_a_orden('sequential', value);
                if (callback){
                    callback();
                }
            });
        }
    },
    get_sequential: function() {
        var sequential = this.config && this.config.secuencial || 0;
        return sequential || 0;
    },
    get_next_sequential: function() {
        var sequential = Math.max(0, Number(this.get_sequential()));
        this.set_sequential(++sequential);
        return sequential;
    },
    add_new_order: function(){
        var order = _super_posmodel.add_new_order.call(this);
        if (order) {
            order.establecer_secuencial(this.get_sequential());
            order.asignar_establecimiento(this.get_establishment());
            order.asignar_tipoemision(this.get_tipoemision());
            order.asignar_puntoemision(this.get_emission_point());
            order.asignar_autorizacion(this.get_authorization());
        }
        return order;
    },
    asignar_campo_a_orden: function(campo, valor){
        var order = _super_posmodel.get_order.call(this);
        if (campo && order) {
            switch (campo){
                case 'establishment': order.asignar_establecimiento(valor); break;
                case 'tipoemision': order.asignar_tipoemision(valor); break;
                case 'emission_point': order.asignar_puntoemision(valor); break;
                case 'authorization': order.asignar_autorizacion(valor); break;
                case 'sequential': order.establecer_secuencial(valor); break;
            }
        }
    },
    guardar_configuracion_en_bd : function(campo, valor, callback){
        var self = this;
        var config_id = self.config ? self.config.id : null;
        if (campo && valor && config_id) {

            var dict_field = {};
            dict_field[campo] = valor;
            if (dict_field) {
                (new Model('pos.config'))
                    .call('save_config_from_pos', [config_id, dict_field])
                        .then(function () {
                            if (callback){
                                callback();
                            }
                        })
                        .fail(function (err, event) {
                            self.gui.show_popup('error', {
                                'title': 'Error al guardar',
                                'body': 'No se pudo guardar el campo "' + campo + '" en el servidor',
                            });
                            event.stopPropagation();
                            event.preventDefault();
                        });
            }
        }
    }
});

/* ********************************************************
Updating point_of_sale.Order
******************************************************** */
var _super_order = PosModels.Order.prototype;
PosModels.Order = PosModels.Order.extend({
    export_as_JSON: function() {
        var json = _super_order.export_as_JSON.apply(this,arguments);
        json.secuencial = this.secuencial;
        json.puntoemision = this.puntoemision;
        json.establecimiento = this.establecimiento;
        json.autorizacion = this.autorizacion;
        json.tipoemision = this.tipoemision;
        return json;
    },
    init_from_JSON: function(json) {
        _super_order.init_from_JSON.apply(this,arguments);
        this.secuencial = json.secuencial;
        this.puntoemision = json.puntoemision;
        this.establecimiento = json.establecimiento;
        this.autorizacion = json.autorizacion;
        this.tipoemision = json.tipoemision;
    },
    export_for_printing: function() {
        var json = _super_order.export_for_printing.apply(this,arguments);
        json.secuencial = this.secuencial;
        json.puntoemision = this.puntoemision;
        json.establecimiento = this.establecimiento;
        json.autorizacion = this.autorizacion;
        json.tipoemision = this.tipoemision;
        return json;
    },
    establecer_secuencial: function(value) {
        if (value) {
            this.secuencial = value;
        }
        this.save_to_db();
    },
    asignar_puntoemision: function(valor) {
        if (valor) {
            this.puntoemision = valor;
        }
        this.save_to_db();
    },
    asignar_establecimiento: function(valor) {
        if (valor) {
            this.establecimiento = valor;
        }
        this.save_to_db();
    },
    asignar_autorizacion: function(valor) {
        if (valor) {
            this.autorizacion = valor;
        }
        this.save_to_db();
    },
    asignar_tipoemision: function (valor){
        if (valor) {
            this.tipoemision = valor;
        }
        this.save_to_db();
    }
});

});