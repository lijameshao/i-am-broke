import aws_cdk as cdk

from fastapi_serverless.fastapi_serverless_stack import FastapiServerlessStack


app = cdk.App()

region = app.node.try_get_context("region") or "us-east-1"
account_id = app.node.try_get_context("account_id")

env = cdk.Environment(account=account_id, region=region)
FastapiServerlessStack(app, "FastApiStack", env=env)

app.synth()
