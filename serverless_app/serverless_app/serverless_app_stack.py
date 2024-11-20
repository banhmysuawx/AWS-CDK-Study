from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct

class ServerlessAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table
        products_table = dynamodb.Table(
            self, "ProductsTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Lambda function
        product_list_function = lambda_.Function(
            self, "ProductListFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset("lambda_src"),
            handler="product_list_function.lambda_handler",
            environment={
                "TABLE_NAME": products_table.table_name
            }
            
        )
        
        #Lambda URL
        product_list_function_url = product_list_function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE
        )
        
        #Grant permission to the lambda function to access the DynamoDB table
        products_table.grant_read_data(product_list_function.role)
        
        #Add the URL to the stack outputs
        CfnOutput(
            self, "ProductListFunctionUrl",
            value=product_list_function_url.url,
            description="URL endpoint for the product list function"
        )