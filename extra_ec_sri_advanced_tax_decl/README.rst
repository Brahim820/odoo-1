.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
SRI - Store taxes to declare.
=============================

This module computes the taxes with all the information you will need to generate all tax declarations for Ecuador, it will compute and store taxes to avoid rounding problems and speed up the process.

Installation
============

To install this module, you need to:

* Add the module to your addons path.
* Install the module as usual.

Configuration
=============

This module doesn't requiere any configuration.

Usage
=====

On module instalation a new button will apear on invoices and refunds to compute the taxes on every invoice line.

This values will be stored with all the information needed to generate the tax declarations.
- This taxes will be consolidated with the invoice taxes to avoid differences.
- The values will be pre-computed in order to speed up the computation on the tax declarations.

Instrucciones de uso
====================


.. Demostración en runbot
.. ======================
.. 
.. .. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
..    :alt: Try me on Runbot
..    :target: https://runbot.odoo-community.org/runbot/repo/github-com-oca-l10n-ecuador-212


Known issues / Roadmap
======================

* There are no known issues.
* The module just classify but the report is not generated yet.

Problemas conocidos y planificación
===================================

* No existen problemas conocidos.
* El módulo permite clasificar los cobros y pagos, sin embargo, el reporte aún está pendiente.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-ecuador/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/l10n-ecuador/issues/new?body=module:%20l10n_ec_femd%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Fábrica de Software Libre <desarrollo@libre.ec>

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
