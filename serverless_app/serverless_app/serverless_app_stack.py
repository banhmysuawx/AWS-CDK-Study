from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    CfnOutput,
    RemovalPolicy,
    Duration,
    aws_cloudwatch as cloudwatch,
)
from constructs import Construct


class ServerlessAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table
        products_table = dynamodb.Table(
            self,
            "ProductsTable",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Lambda function
        product_list_function = lambda_.Function(
            self,
            "ProductListFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset("lambda_src"),
            handler="product_list_function.lambda_handler",
            environment={"TABLE_NAME": products_table.table_name},
        )

        # Grant permission to the lambda function to access the DynamoDB table
        # products_table.grant_read_data(product_list_function.role)

        # Lambda URL
        product_list_function_url = product_list_function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE
        )

        # Add the URL to the stack outputs
        CfnOutput(
            self,
            "ProductListFunctionUrl",
            value=product_list_function_url.url,
            description="URL endpoint for the product list function",
        )

        # Configure metrics to monitor the lambda function
        errors_metric = product_list_function.metric_errors(
            label="ProductListFunctionErrors",
            period=Duration.minutes(5),
            statistic=cloudwatch.Stats.SUM,
        )

        # Create an alarm to monitor the errors metric
        errors_metric.create_alarm(
            self,
            "ProductListErrorsAlarm",
            evaluation_periods=1,
            threshold=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.IGNORE,
        )
