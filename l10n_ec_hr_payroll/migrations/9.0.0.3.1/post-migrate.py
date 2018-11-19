#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def fix_contract_job_history(env):
    contract_ids = env["hr.contract"].search([("hist_job_ids", "!=", False)])
    for contract in contract_ids:
        job_ids = contract.hist_job_ids.sorted(lambda x: x.date)
        for job in job_ids:
            old = job_ids.search(
                [("date", "<", job.date), ("contract_id", "=", job.contract_id.id)],
                limit=1,
            )
            if old:
                job.date_from = old.date
            else:
                job.date_from = job.contract_id.date_start
            job.date_to = job.date


def fix_contract_wage_history(env):
    contract_ids = env["hr.contract"].search([("hist_wage_ids", "!=", False)])
    for contract in contract_ids:
        wage_ids = contract.hist_wage_ids.sorted(lambda x: x.date)
        for wage in wage_ids:
            old = wage_ids.search(
                [("date", "<", wage.date), ("contract_id", "=", wage.contract_id.id)],
                limit=1,
            )
            if old:
                wage.date_from = old.date
            else:
                wage.date_from = wage.contract_id.date_start
            wage.date_to = wage.date


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    fix_contract_job_history(env)
    fix_contract_wage_history(env)
