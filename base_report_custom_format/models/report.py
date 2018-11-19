# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ReportCustomFormat(models.Model):
    _name = 'report.custom.format'

    name = fields.Char('Name', )

    # Page layout
    image = fields.Binary()
    header = fields.Html('Header', )
    footer = fields.Html('Footer', )

    page_orientation = fields.Selection([
        ('portrait', 'portrait'),
        ('landscape', 'landscape', )
    ], default='portrait', )
    page_padding_top = fields.Integer('Padding top (mm)', default=15, )
    page_padding_right = fields.Integer('Padding right (mm)', default=15, )
    page_padding_bottom = fields.Integer('Padding bottom (mm)', default=15, )
    page_padding_left = fields.Integer('Padding left (mm)', default=15, )
    page_font_size = fields.Integer('Font size (pt)', default=10, )
    page_line_height = fields.Integer('Line spacing (%)', default=120, )
    page_font_family = fields.Selection([
        ('Arial', 'Arial'),
        ('Calibri', 'Calibri'),
        ('Open+Sans', 'Open Sans'),
        ('Roboto+Condensed', 'Roboto Condensed'),
        ('Sacramento', 'Sacramento'),
        ('Play', 'Play'),
        ('Raleway', 'Raleway'),
        ('Titillium+Web', 'Titillium Web'),
        ('Orbitron', 'Orbitron'),
    ], default='Arial', )

    page_style = fields.Char(
        'Page style', compute="compute_page_settings", store=True, )

    @api.depends('page_padding_top', 'page_padding_right', 'page_padding_bottom',
                 'page_padding_left', 'page_font_size', 'page_font_family')
    def compute_page_settings(self):
        padding = "padding: %smm %smm %smm %smm;" % (
            self.page_padding_top or 0,
            self.page_padding_right or 0,
            self.page_padding_bottom or 0,
            self.page_padding_left or 0,
        )

        font_size = "font-size: %spt;" % self.page_font_size

        font_family = "font-family: '%s', sans-serif;" % self.page_font_family

        line_height = "line-height: %s" % self.page_line_height + "%;"

        self.page_style = ' '.join([padding, font_size, font_family,
                                    line_height])

    copies = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    ], default='1', )
    separator_style = fields.Char(string="Separator style", )


class ReportFormatSelector(models.AbstractModel):
    _name = 'report.format.selector'

    # Class to inherit and add new report selector.
