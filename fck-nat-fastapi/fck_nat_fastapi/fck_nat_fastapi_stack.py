from aws_cdk import (
    Duration,
    Stack,
    BundlingOptions,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_lambda as lambda_,
)

from constructs import Construct

from aws_cdk.aws_apigatewayv2 import (
    HttpApi,
    HttpMethod,
    CorsHttpMethod,
    CorsPreflightOptions,
)
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration

import cdk_fck_nat


class FckNatFastapiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        nat_gateway_provider = cdk_fck_nat.FckNatInstanceProvider(
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G, ec2.InstanceSize.NANO
            ),
        )

        vpc = ec2.Vpc(self, "vpc", nat_gateway_provider=nat_gateway_provider, max_azs=1)

        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole"
            )
        )

        fastapi_handler_security_group = ec2.SecurityGroup(
            self,
            "FastApiHandlerSecurityGroup",
            vpc=vpc,
            description="Allow ssh access to ec2 instances",
            allow_all_outbound=True,
        )
        nat_gateway_provider.security_group.add_ingress_rule(
            fastapi_handler_security_group,
            connection=ec2.Port.tcp(443),
            description="Allow internet traffic initiated from FastAPI lambda",
        )

        fastapi_handler = lambda_.Function(
            self,
            "FastApiHandler",
            code=lambda_.Code.from_asset(
                "lambda",
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output",
                    ],
                ),
            ),
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            # Comment the below line out unless you are using ARM64 based system to build the lambda image.
            architecture=lambda_.Architecture.ARM_64,
            role=lambda_role,
            vpc=vpc,
            security_groups=[fastapi_handler_security_group],
            memory_size=128,
            timeout=Duration.seconds(29),
        )

        http_api = HttpApi(
            self,
            "HttpApiGateway",
            cors_preflight=CorsPreflightOptions(
                allow_headers=["Authorization", "Content-Type"],
                allow_methods=[
                    CorsHttpMethod.OPTIONS,
                    CorsHttpMethod.GET,
                    CorsHttpMethod.HEAD,
                    CorsHttpMethod.POST,
                ],
                allow_origins=["*"],
                max_age=Duration.days(10),
            ),
        )
        http_api.add_routes(
            path="/{proxy+}",
            methods=[HttpMethod.ANY],
            integration=HttpLambdaIntegration(
                "ApiIntegration", handler=fastapi_handler
            ),
        )
