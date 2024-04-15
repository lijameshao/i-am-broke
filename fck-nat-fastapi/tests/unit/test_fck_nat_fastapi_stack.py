import aws_cdk as core
import aws_cdk.assertions as assertions

from fck_nat_fastapi.fck_nat_fastapi_stack import FckNatFastapiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in fck_nat_fastapi/fck_nat_fastapi_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FckNatFastapiStack(app, "fck-nat-fastapi")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
