#!/usr/bin/env python
# -*- coding: utf-8 -*-
{
    "name": "Batch Payments Processing From File",
    "summary": "Process Payments in Batch from File",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "Edison Ibáñez",
    "category": "Generic Modules/Payment",
    "website": "",
    "depends": [
        "account_payment_batch_process",
    ],
    "data": [
        "views/account_payment_view.xml",
        "wizard/invoice_batch_process_file_view.xml",
    ],
    "installable": True,
}
