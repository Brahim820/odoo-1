.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Ecuador's POS SRI
=================


Installation
============

To install this module, you need to:

* Be sure that you have libxml2-utils installed, if not, try:
    (sudo) apt-get install libxml2-utils
* Be sure that you have stdnum python library installed, if not, try:
    (sudo) pip install python-stdnum

Configuration
=============

* Add a default property_account_receivable_id and property_account_payable_id country, city, etc on res.partner.


Road map
========

* Remove the label "TAX ID" form ClientDetailsEdit
* On client creation, use the country code to update the vat if no country code is set and leave EC as fall back.
* Add defaults autorizacion, comprobante and secuencial to the invoice.
* Compute the default fiscal position using the RUC numbers.

Usage
=====



Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Fábrica de Software Libre <desarrollo@libre.ec>
* Jonathan Finlay <jfinlay@risuep.net>
* Edison Ibañez <edison@openmailbox.org>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org... image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3
