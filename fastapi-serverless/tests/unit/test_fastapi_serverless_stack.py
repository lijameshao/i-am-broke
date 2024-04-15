import aws_cdk as core
import aws_cdk.assertions as assertions

from fastapi_serverless.fastapi_serverless_stack import FastapiServerlessStack

# example tests. To run these tests, uncomment this file along with the example
# resource in fastapi_serverless/fastapi_serverless_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FastapiServerlessStack(app, "fastapi-serverless")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
