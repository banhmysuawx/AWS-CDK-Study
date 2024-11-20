from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct


class SampleAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        my_vpc = ec2.CfnVPC(
            self,
            "MyVPC",
            cidr_block="10.0.0.0/16",
            enable_dns_support=True,
            enable_dns_hostnames=True,
        )

        my_internet_gateway = ec2.CfnInternetGateway(self, "MyInternetGateway")

        # Attach internet gateway to VPC
        ec2.CfnVPCGatewayAttachment(
            self,
            "MyVPCGatewayAttachment",
            vpc_id=my_vpc.attr_vpc_id,
            internet_gateway_id=my_internet_gateway.attr_internet_gateway_id,
        )

        subnet_config = [
            {"cidrMask": 24, "name": "Ingress 1", "public": True},
            {"cidrMask": 24, "name": "Ingress 2", "public": True},
            {"cidrMask": 24, "name": "Application 2", "public": False},
            {"cidrMask": 24, "name": "Application 3", "public": False},
        ]

        for index, config in enumerate(subnet_config):
            subnet_resource = ec2.CfnSubnet(
                self,
                f"MySubnet{index+1}",
                vpc_id=my_vpc.attr_vpc_id,
                cidr_block=f"10.0.{index}.0/{config['cidrMask']}",
                availability_zone=Stack.availability_zones.fget(self)[index % 2],
                map_public_ip_on_launch=config["public"],
            )

            # create route table
            route_table = ec2.CfnRouteTable(
                self, f"MyRouteTable{index}", vpc_id=my_vpc.attr_vpc_id
            )

            # Associate route table with subnet
            ec2.CfnSubnetRouteTableAssociation(
                self,
                f"MySubnetRouteTableAssociation{index}",
                route_table_id=route_table.attr_route_table_id,
                subnet_id=subnet_resource.attr_subnet_id,
            )

            # If subnet is public, create route to internet gateway
            if config["public"]:
                ec2.CfnRoute(
                    self,
                    f"MyRoute{index}",
                    route_table_id=route_table.attr_route_table_id,
                    destination_cidr_block="0.0.0.0/0",
                    gateway_id=my_internet_gateway.attr_internet_gateway_id,
                )


class L2ConstructsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Tạo VPC với L2 construct
        my_vpc = ec2.Vpc(
            self, "MyVpc", nat_gateways=0  # Tạo isolated subnets thay vì NAT gateways
        )
