#!/usr/bin/env python3
import aws_cdk as cdk

from fck_nat_fastapi.fck_nat_fastapi_stack import FckNatFastapiStack

app = cdk.App()

region = app.node.try_get_context("region") or "us-east-1"
account_id = app.node.try_get_context("account_id")

env = cdk.Environment(account=account_id, region=region)
FckNatFastapiStack(app, "FckNatFastapiStack", env=env)

app.synth()
