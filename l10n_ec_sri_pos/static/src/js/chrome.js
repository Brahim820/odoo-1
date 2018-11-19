odoo.define('l10n_ec_sri_pos.chrome', function (require) {
"use strict";

var chrome = require('point_of_sale.chrome');

var core = require('web.core');
var _t = core._t;

/* ********************************************************
chrome.Chrome
******************************************************** */
    chrome.Chrome.include({
        mostrar_menu_autorizacion: function(){
            var self = this;
            self.pos.gui.show_popup('sri_pos_selection',{
                   title: _t('Authorization'),
                   list: self.get_authorization_options(self),
                   confirm: function(item) {
                       if (item === 'establishment'){
                           self.action_authorization_option_establishment(self);
                       } else if (item === 'emission_type'){
                           self.action_authorization_option_emission_type(self);
                       } else if (item === 'emission_point'){
                           self.action_authorization_option_emission_point(self);
                       } else if (item === 'authorization'){
                           self.action_authorization_option_authorization(self);
                       } else if (item === 'sequential'){
                           self.action_authorization_option_sequential(self);
                       }
                   },
                   cancel: function(){
                       // user chose nothing
                   }
                });
        },
        get_label_tipoemision: function(tipoemision){
            if (tipoemision === 'F'){
                return _t('Physical');
            } else {
                return _t('Electronic');
            }
        },
        get_authorization_options: function(self){
            var establishment = self.pos.get_establishment();
            var tipoemision = self.pos.get_tipoemision();
            var label_tipoemision = self.get_label_tipoemision(tipoemision);

            var emission_point = self.pos.get_emission_point();
            var authorization = self.pos.get_authorization();
            var sequential = self.pos.get_sequential();

            var option_list = [
               { label: _t('Establishment') + ' [' + establishment + ']',  item: 'establishment' },
               { label: _t('Emission Point') + ' [' + emission_point + ']',  item: 'emission_point' },
               { label: _t('Emission Type') + ' [' + label_tipoemision + ']',  item: 'emission_type' },
            ];

            if (tipoemision === 'F'){
                option_list.push({ label: _t('Authorization') + ' [' + authorization + ']',  item: 'authorization' });
                option_list.push({ label: _t('Sequential') + ' [' + sequential + ']',  item: 'sequential' });
            }

            return option_list;
        },
        action_authorization_option_establishment: function(self){
            self.gui.show_popup('number',{
                'title': 'Establecimiento',
                'value': self.pos.get_establishment(),
                'confirm': function(value) {
                    value = Math.max(1,Number(value));
                    self.pos.set_establishment(value, function () {
                        self.mostrar_menu_autorizacion();
                    });
                },
                cancel: function(){
                    self.mostrar_menu_autorizacion();
                }
            });
        },
        action_authorization_option_emission_type: function(self){
            self.gui.show_popup('selection',{
                'title': 'Tipo de emisión',
                list: [
                       { label: _t('Physical billing'),  item: 'F' },
                       { label: _t('Electronic billing'),  item: 'E' },
                   ],
                confirm: function(item) {
                    self.pos.set_tipoemision(item, function () {
                        self.mostrar_menu_autorizacion();
                    });
                },
                cancel: function(){
                    self.mostrar_menu_autorizacion();
                }
            });
        },
        action_authorization_option_authorization: function(self){
            self.gui.show_popup('number',{
                'title': _t('Authorization'),
                'value': self.pos.get_authorization(),
                'confirm': function(value) {
                    value = Math.max(1, Number(value));
                    self.pos.set_authorization(value, function () {
                        self.mostrar_menu_autorizacion();
                    });
                },
                cancel: function(){
                    self.mostrar_menu_autorizacion();
                }
            });
        },
        action_authorization_option_sequential: function(self){
            self.gui.show_popup('number',{
                'title': _t('Sequential'),
                'value': self.pos.get_sequential(),
                'confirm': function(value) {
                    value = Math.max(1, Number(value));
                    self.pos.set_sequential(value, function () {
                        self.mostrar_menu_autorizacion();
                    });
                },
                cancel: function(){
                    self.mostrar_menu_autorizacion();
                }
            });
        },
        action_authorization_option_emission_point: function(self){
            self.gui.show_popup('number',{
                'title': 'Punto de emisión',
                'value': self.pos.get_emission_point(),
                'confirm': function(value) {
                    value = Math.max(1, Number(value));
                    self.pos.set_emission_point(value, function () {
                        self.mostrar_menu_autorizacion();
                    });
                },
                cancel: function(){
                    self.mostrar_menu_autorizacion();
                }
            });
        },
        renderElement: function(){
            this._super();
            this.$('#pos-authorization').click(this.mostrar_menu_autorizacion.bind(this));
        },
    });

});
