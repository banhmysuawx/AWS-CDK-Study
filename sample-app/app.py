#!/usr/bin/env python3
import os

import aws_cdk as cdk

from sample_app.sample_app_stack import SampleAppStack,L2ConstructsStack


app = cdk.App()
SampleAppStack(
    app,
    "SampleAppStack",
)

L2ConstructsStack(
    app,
    "L2ConstructsStack",
)

app.synth()
