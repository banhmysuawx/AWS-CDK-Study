#!/usr/bin/env python3
import os

import aws_cdk as cdk

from serverless_app.serverless_app_stack import (
    ServerlessAppStack,
    ServerlessAppStackUsingL3,
)


app = cdk.App()
ServerlessAppStack(
    app,
    "ServerlessAppStack",
)
ServerlessAppStackUsingL3(
    app,
    "ServerlessAppStackUsingL3",
)

app.synth()
