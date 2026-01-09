#!/bin/bash
# AWS EC2 RDP Troubleshooting Commands
# Date: 2026-01-04
# Issue: RDP Error 0x204 - Private Subnet Access Problem



---
This command will return every configuration detail for that specific instance ID in JSON format.
--
~ $ aws ec2 describe-instances --instance-ids i-0e3229b9ac12f5a39
{
    "Reservations": [
        {
            "ReservationId": "r-00857f6f7347d8099",
            "OwnerId": "457451358907",
            "Groups": [],
            "Instances": [
                {
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": {
                                "AttachTime": "2026-01-03T02:49:56+00:00",
                                "DeleteOnTermination": true,
                                "Status": "attached",
                                "VolumeId": "vol-0df0691bddf4bc2cf"
                            }
                        }
                    ],
                    "ClientToken": "f852df64-7e10-4727-a5f8-085be33be265",
                    "EbsOptimized": true,
                    "EnaSupport": true,
                    "Hypervisor": "xen",
                    "IamInstanceProfile": {
                        "Arn": "arn:aws:iam::457451358907:instance-profile/AmazonSSMManagedInstanceCore",
                        "Id": "AIPAWVARZZK5T7PW6W4ZJ"
                    },
                    "NetworkInterfaces": [
                        {
                            "Attachment": {
                                "AttachTime": "2026-01-03T02:49:56+00:00",
                                "AttachmentId": "eni-attach-05ff2ed10616a3755",
                                "DeleteOnTermination": true,
                                "DeviceIndex": 0,
                                "Status": "attached",
                                "NetworkCardIndex": 0
                            },
                            "Description": "",
                            "Groups": [
                                {
                                    "GroupId": "sg-078968af2967efd66",
                                    "GroupName": "AD-DC-SG"
                                }
                            ],
                            "Ipv6Addresses": [],
                            "MacAddress": "12:c3:f2:34:4c:31",
                            "NetworkInterfaceId": "eni-091ab1a2df2d5d2e7",
                            "OwnerId": "457451358907",
                            "PrivateIpAddress": "10.0.2.8",
                            "PrivateIpAddresses": [
                                {
                                    "Primary": true,
                                    "PrivateIpAddress": "10.0.2.8"
                                }
                            ],
                            "SourceDestCheck": true,
                            "Status": "in-use",
                            "SubnetId": "subnet-048bc52084885ebae",
                            "VpcId": "vpc-0517d5e295a732156",
                            "InterfaceType": "interface",
                            "Operator": {
                                "Managed": false
                            }
                        }
                    ],
                    "RootDeviceName": "/dev/sda1",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [
                        {
                            "GroupId": "sg-078968af2967efd66",
                            "GroupName": "AD-DC-SG"
                        }
                    ],
                    "SourceDestCheck": true,
                    "StateReason": {
                        "Code": "Client.UserInitiatedShutdown",
                        "Message": "Client.UserInitiatedShutdown: User initiated shutdown"
                    },
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "WinSvr25"
                        }
                    ],
                    "VirtualizationType": "hvm",
                    "CpuOptions": {
                        "CoreCount": 1,
                        "ThreadsPerCore": 2
                    },
                    "CapacityReservationSpecification": {
                        "CapacityReservationPreference": "open"
                    },
                    "HibernationOptions": {
                        "Configured": false
                    },
                    "MetadataOptions": {
                        "State": "applied",
                        "HttpTokens": "required",
                        "HttpPutResponseHopLimit": 2,
                        "HttpEndpoint": "enabled",
                        "HttpProtocolIpv6": "disabled",
                        "InstanceMetadataTags": "disabled"
                    },
                    "EnclaveOptions": {
                        "Enabled": false
                    },
                    "BootMode": "uefi",
                    "PlatformDetails": "Windows",
                    "UsageOperation": "RunInstances:0002",
                    "UsageOperationUpdateTime": "2026-01-03T02:49:56+00:00",
                    "PrivateDnsNameOptions": {
                        "HostnameType": "ip-name",
                        "EnableResourceNameDnsARecord": false,
                        "EnableResourceNameDnsAAAARecord": false
                    },
                    "MaintenanceOptions": {
                        "AutoRecovery": "default",
                        "RebootMigration": "default"
                    },
                    "CurrentInstanceBootMode": "uefi",
                    "NetworkPerformanceOptions": {
                        "BandwidthWeighting": "default"
                    },
                    "Operator": {
                        "Managed": false
                    },
                    "InstanceId": "i-0e3229b9ac12f5a39",
                    "ImageId": "ami-06777e7ef7441deff",
                    "State": {
                        "Code": 80,
                        "Name": "stopped"
                    },
                    "PrivateDnsName": "ip-10-0-2-8.ec2.internal",
                    "PublicDnsName": "",
                    "StateTransitionReason": "User initiated (2026-01-04 20:37:50 GMT)",
                    "KeyName": "ad_dc_key",
                    "AmiLaunchIndex": 0,
                    "ProductCodes": [],
                    "InstanceType": "c7i-flex.large",
                    "LaunchTime": "2026-01-04T19:04:08+00:00",
                    "Placement": {
                        "AvailabilityZoneId": "use1-az2",
                        "GroupName": "",
                        "Tenancy": "default",
                        "AvailabilityZone": "us-east-1a"
                    },
                    "Platform": "windows",
                    "Monitoring": {
                        "State": "disabled"
                    },
                    "SubnetId": "subnet-048bc52084885ebae",
                    "VpcId": "vpc-0517d5e295a732156",
                    "PrivateIpAddress": "10.0.2.8"
                }
            ]
        }
    ]
}

-------------

If you want a cleaner, organized view (similar to the summary you see in the console), use the --output table flag:

----

~ $ aws ec2 describe-instances --instance-ids i-0e3229b9ac12f5a39 --output table
------------------------------------------------------------------------------------------
|                                    DescribeInstances                                   |
+----------------------------------------------------------------------------------------+
||                                     Reservations                                     ||
|+-----------------------------------+--------------------------------------------------+|
||  OwnerId                          |  457451358907                                    ||
||  ReservationId                    |  r-00857f6f7347d8099                             ||
|+-----------------------------------+--------------------------------------------------+|
|||                                      Instances                                     |||
||+-------------------------------+----------------------------------------------------+||
|||  AmiLaunchIndex               |  0                                                 |||
|||  Architecture                 |  x86_64                                            |||
|||  BootMode                     |  uefi                                              |||
|||  ClientToken                  |  f852df64-7e10-4727-a5f8-085be33be265              |||
|||  CurrentInstanceBootMode      |  uefi                                              |||
|||  EbsOptimized                 |  True                                              |||
|||  EnaSupport                   |  True                                              |||
|||  Hypervisor                   |  xen                                               |||
|||  ImageId                      |  ami-06777e7ef7441deff                             |||
|||  InstanceId                   |  i-0e3229b9ac12f5a39                               |||
|||  InstanceType                 |  c7i-flex.large                                    |||
|||  KeyName                      |  ad_dc_key                                         |||
|||  LaunchTime                   |  2026-01-04T19:04:08+00:00                         |||
|||  Platform                     |  windows                                           |||
|||  PlatformDetails              |  Windows                                           |||
|||  PrivateDnsName               |  ip-10-0-2-8.ec2.internal                          |||
|||  PrivateIpAddress             |  10.0.2.8                                          |||
|||  PublicDnsName                |                                                    |||
|||  RootDeviceName               |  /dev/sda1                                         |||
|||  RootDeviceType               |  ebs                                               |||
|||  SourceDestCheck              |  True                                              |||
|||  StateTransitionReason        |  User initiated (2026-01-04 20:37:50 GMT)          |||
|||  SubnetId                     |  subnet-048bc52084885ebae                          |||
|||  UsageOperation               |  RunInstances:0002                                 |||
|||  UsageOperationUpdateTime     |  2026-01-03T02:49:56+00:00                         |||
|||  VirtualizationType           |  hvm                                               |||
|||  VpcId                        |  vpc-0517d5e295a732156                             |||
||+-------------------------------+----------------------------------------------------+||
||||                                BlockDeviceMappings                               ||||
|||+------------------------------------------+---------------------------------------+|||
||||  DeviceName                              |  /dev/sda1                            ||||
|||+------------------------------------------+---------------------------------------+|||
|||||                                       Ebs                                      |||||
||||+----------------------------------+---------------------------------------------+||||
|||||  AttachTime                      |  2026-01-03T02:49:56+00:00                  |||||
|||||  DeleteOnTermination             |  True                                       |||||
|||||  Status                          |  attached                                   |||||
|||||  VolumeId                        |  vol-0df0691bddf4bc2cf                      |||||
||||+----------------------------------+---------------------------------------------+||||
||||                         CapacityReservationSpecification                         ||||
|||+------------------------------------------------------------------+---------------+|||
||||  CapacityReservationPreference                                   |  open         ||||
|||+------------------------------------------------------------------+---------------+|||
||||                                    CpuOptions                                    ||||
|||+----------------------------------------------------------------+-----------------+|||
||||  CoreCount                                                     |  1              ||||
||||  ThreadsPerCore                                                |  2              ||||
|||+----------------------------------------------------------------+-----------------+|||
||||                                  EnclaveOptions                                  ||||
|||+--------------------------------------------+-------------------------------------+|||
||||  Enabled                                   |  False                              ||||
|||+--------------------------------------------+-------------------------------------+|||
||||                                HibernationOptions                                ||||
|||+-------------------------------------------------+--------------------------------+|||
||||  Configured                                     |  False                         ||||
|||+-------------------------------------------------+--------------------------------+|||
||||                                IamInstanceProfile                                ||||
|||+-----+----------------------------------------------------------------------------+|||
||||  Arn|  arn:aws:iam::457451358907:instance-profile/AmazonSSMManagedInstanceCore   ||||
||||  Id |  AIPAWVARZZK5T7PW6W4ZJ                                                     ||||
|||+-----+----------------------------------------------------------------------------+|||
||||                                MaintenanceOptions                                ||||
|||+---------------------------------------------------+------------------------------+|||
||||  AutoRecovery                                     |  default                     ||||
||||  RebootMigration                                  |  default                     ||||
|||+---------------------------------------------------+------------------------------+|||
||||                                  MetadataOptions                                 ||||
|||+--------------------------------------------------------+-------------------------+|||
||||  HttpEndpoint                                          |  enabled                ||||
||||  HttpProtocolIpv6                                      |  disabled               ||||
||||  HttpPutResponseHopLimit                               |  2                      ||||
||||  HttpTokens                                            |  required               ||||
||||  InstanceMetadataTags                                  |  disabled               ||||
||||  State                                                 |  applied                ||||
|||+--------------------------------------------------------+-------------------------+|||
||||                                    Monitoring                                    ||||
|||+----------------------------------+-----------------------------------------------+|||
||||  State                           |  disabled                                     ||||
|||+----------------------------------+-----------------------------------------------+|||
||||                                 NetworkInterfaces                                ||||
|||+-----------------------------------+----------------------------------------------+|||
||||  Description                      |                                              ||||
||||  InterfaceType                    |  interface                                   ||||
||||  MacAddress                       |  12:c3:f2:34:4c:31                           ||||
||||  NetworkInterfaceId               |  eni-091ab1a2df2d5d2e7                       ||||
||||  OwnerId                          |  457451358907                                ||||
||||  PrivateIpAddress                 |  10.0.2.8                                    ||||
||||  SourceDestCheck                  |  True                                        ||||
||||  Status                           |  in-use                                      ||||
||||  SubnetId                         |  subnet-048bc52084885ebae                    ||||
||||  VpcId                            |  vpc-0517d5e295a732156                       ||||
|||+-----------------------------------+----------------------------------------------+|||
|||||                                   Attachment                                   |||||
||||+--------------------------------+-----------------------------------------------+||||
|||||  AttachTime                    |  2026-01-03T02:49:56+00:00                    |||||
|||||  AttachmentId                  |  eni-attach-05ff2ed10616a3755                 |||||
|||||  DeleteOnTermination           |  True                                         |||||
|||||  DeviceIndex                   |  0                                            |||||
|||||  NetworkCardIndex              |  0                                            |||||
|||||  Status                        |  attached                                     |||||
||||+--------------------------------+-----------------------------------------------+||||
|||||                                     Groups                                     |||||
||||+---------------------------+----------------------------------------------------+||||
|||||  GroupId                  |  sg-078968af2967efd66                              |||||
|||||  GroupName                |  AD-DC-SG                                          |||||
||||+---------------------------+----------------------------------------------------+||||
|||||                                    Operator                                    |||||
||||+-------------------------------------------+------------------------------------+||||
|||||  Managed                                  |  False                             |||||
||||+-------------------------------------------+------------------------------------+||||
|||||                               PrivateIpAddresses                               |||||
||||+-------------------------------------------------+------------------------------+||||
|||||  Primary                                        |  True                        |||||
|||||  PrivateIpAddress                               |  10.0.2.8                    |||||
||||+-------------------------------------------------+------------------------------+||||
||||                             NetworkPerformanceOptions                            ||||
|||+------------------------------------------------------+---------------------------+|||
||||  BandwidthWeighting                                  |  default                  ||||
|||+------------------------------------------------------+---------------------------+|||
||||                                     Operator                                     ||||
|||+--------------------------------------------+-------------------------------------+|||
||||  Managed                                   |  False                              ||||
|||+--------------------------------------------+-------------------------------------+|||
||||                                     Placement                                    ||||
|||+-------------------------------------------------+--------------------------------+|||
||||  AvailabilityZone                               |  us-east-1a                    ||||
||||  AvailabilityZoneId                             |  use1-az2                      ||||
||||  GroupName                                      |                                ||||
||||  Tenancy                                        |  default                       ||||
|||+-------------------------------------------------+--------------------------------+|||
||||                               PrivateDnsNameOptions                              ||||
|||+--------------------------------------------------------------+-------------------+|||
||||  EnableResourceNameDnsAAAARecord                             |  False            ||||
||||  EnableResourceNameDnsARecord                                |  False            ||||
||||  HostnameType                                                |  ip-name          ||||
|||+--------------------------------------------------------------+-------------------+|||
||||                                  SecurityGroups                                  ||||
|||+----------------------------+-----------------------------------------------------+|||
||||  GroupId                   |  sg-078968af2967efd66                               ||||
||||  GroupName                 |  AD-DC-SG                                           ||||
|||+----------------------------+-----------------------------------------------------+|||
||||                                       State                                      ||||
|||+---------------------------------+------------------------------------------------+|||
||||  Code                           |  80                                            ||||
||||  Name                           |  stopped                                       ||||
|||+---------------------------------+------------------------------------------------+|||
||||                                    StateReason                                   ||||
|||+------------+---------------------------------------------------------------------+|||
||||  Code      |  Client.UserInitiatedShutdown                                       ||||
||||  Message   |  Client.UserInitiatedShutdown: User initiated shutdown              ||||
|||+------------+---------------------------------------------------------------------+|||
||||                                       Tags                                       ||||
|||+----------------------------------+-----------------------------------------------+|||
||||  Key                             |  Name                                         ||||
||||  Value                           |  WinSvr25                                     ||||
|||+----------------------------------+-----------------------------------------------+|||


~ $ aws ec2 describe-security-groups --group-ids sg-078968af2967efd66 \
> --query 'SecurityGroups[*].{Name:GroupName,Vpc:VpcId,Desc:Description}' \
> --output table --region us-east-1
-------------------------------------------------------------------------------------------
|                                 DescribeSecurityGroups                                  |
+---------------------------------------------------+-----------+-------------------------+
|                       Desc                        |   Name    |           Vpc           |
+---------------------------------------------------+-----------+-------------------------+
|  launch-wizard-5 created 2026-01-03T02:18:46.458Z |  AD-DC-SG |  vpc-0517d5e295a732156  |
+---------------------------------------------------+-----------+-------------------------+
~ $ aws ec2 describe-security-groups --group-ids sg-078968af2967efd66 --region us-east-1
{
    "SecurityGroups": [
        {
            "GroupId": "sg-078968af2967efd66",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "UserIdGroupPairs": [],
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": []
                }
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "AD-DC-SG"
                }
            ],
            "VpcId": "vpc-0517d5e295a732156",
            "SecurityGroupArn": "arn:aws:ec2:us-east-1:457451358907:security-group/sg-078968af2967efd66",
            "OwnerId": "457451358907",
            "GroupName": "AD-DC-SG",
            "Description": "launch-wizard-5 created 2026-01-03T02:18:46.458Z",
            "IpPermissions": [
                {
                    "IpProtocol": "-1",
                    "UserIdGroupPairs": [],
                    "IpRanges": [
                        {
                            "CidrIp": "10.0.0.0/16"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": []
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 3389,
                    "ToPort": 3389,
                    "UserIdGroupPairs": [],
                    "IpRanges": [
                        {
                            "CidrIp": "98.116.74.198/32"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": []
                }
            ]
        }
    ]
}
(END)


-------------------
Quick Summary (Table View) on the Security group.
-------------

 $ aws ec2 describe-security-groups --group-ids sg-078968af2967efd66 \
> --query 'SecurityGroups[*].{Name:GroupName,Vpc:VpcId,Desc:Description}' \
> --output table --region us-east-1
-------------------------------------------------------------------------------------------
|                                 DescribeSecurityGroups                                  |
+---------------------------------------------------+-----------+-------------------------+
|                       Desc                        |   Name    |           Vpc           |
+---------------------------------------------------+-----------+-------------------------+
|  launch-wizard-5 created 2026-01-03T02:18:46.458Z |  AD-DC-SG |  vpc-0517d5e295a732156  |
+---------------------------------------------------+-----------+-------------------------+

------
look into the details of the Security Group (sg-078968af2967efd66)  in format JSON
----

~ $ aws ec2 describe-security-groups --group-ids sg-078968af2967efd66 --region us-east-1
{
    "SecurityGroups": [
        {
            "GroupId": "sg-078968af2967efd66",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "UserIdGroupPairs": [],
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": []
                }
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "AD-DC-SG"
                }
            ],
            "VpcId": "vpc-0517d5e295a732156",
            "SecurityGroupArn": "arn:aws:ec2:us-east-1:457451358907:security-group/sg-078968af2967efd66",
            "OwnerId": "457451358907",
            "GroupName": "AD-DC-SG",
            "Description": "launch-wizard-5 created 2026-01-03T02:18:46.458Z",
            "IpPermissions": [
                {
                    "IpProtocol": "-1",
                    "UserIdGroupPairs": [],
                    "IpRanges": [
                        {
                            "CidrIp": "10.0.0.0/16"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": []
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 3389,
                    "ToPort": 3389,
                    "UserIdGroupPairs": [],
                    "IpRanges": [
                        {
                            "CidrIp": "98.116.74.198/32"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": []
                }
            ]
        }
    ]
}

~ $ aws ec2 describe-route-tables \
>   --filters "Name=vpc-id,Values=vpc-0517d5e295a732156" \
>   --region us-east-1

{
    "RouteTables": [
        {
            "Associations": [
                {
                    "Main": false,
                    "RouteTableAssociationId": "rtbassoc-02a69631f5ec2f982",
                    "RouteTableId": "rtb-08e60668585fd2dd0",
                    "SubnetId": "subnet-0a2f8ae111d156552",
                    "AssociationState": {
                        "State": "associated"
                    }
                }
            ],
            "PropagatingVgws": [],
            "RouteTableId": "rtb-08e60668585fd2dd0",
            "Routes": [
                {
                    "DestinationCidrBlock": "10.0.0.0/16",
                    "GatewayId": "local",
                    "Origin": "CreateRouteTable",
                    "State": "active"
                },
                {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": "igw-056478d77867b53a6",
                    "Origin": "CreateRoute",
                    "State": "active"
                }
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "AD-Pub-RT"
                }
            ],
            "VpcId": "vpc-0517d5e295a732156",
            "OwnerId": "457451358907"
        },
        {
            "Associations": [
                {
                    "Main": true,
                    "RouteTableAssociationId": "rtbassoc-055edf9085eadc9f1",
                    "RouteTableId": "rtb-0c500fce31e3bf721",
                    "AssociationState": {
                        "State": "associated"
                    }
                }
            ],
            "PropagatingVgws": [],
            "RouteTableId": "rtb-0c500fce31e3bf721",
            "Routes": [
                {
                    "DestinationCidrBlock": "10.0.0.0/16",
                    "GatewayId": "local",
                    "Origin": "CreateRouteTable",
                    "State": "active"
                }
            ],
            "Tags": [],
            "VpcId": "vpc-0517d5e295a732156",
            "OwnerId": "457451358907"
        }
    ]
}
 
--
View Routes in a Clean Table Format
--

~ $ aws ec2 describe-route-tables \
>   --filters "Name=vpc-id,Values=vpc-0517d5e295a732156" \
>   --query 'RouteTables[*].{ID:RouteTableId,Routes:Routes[*].{Dest:DestinationCidrBlock,Target:GatewayId}}' \
>   --output table \
>   --region us-east-1
--------------------------------------------
|            DescribeRouteTables           |
+------------------------------------------+
|                    ID                    |
+------------------------------------------+
|  rtb-08e60668585fd2dd0                   |
+------------------------------------------+
||                 Routes                 ||
|+--------------+-------------------------+|
||     Dest     |         Target          ||
|+--------------+-------------------------+|
||  10.0.0.0/16 |  local                  ||
||  0.0.0.0/0   |  igw-056478d77867b53a6  ||
|+--------------+-------------------------+|
|            DescribeRouteTables           |
+------------------------------------------+
|                    ID                    |
+------------------------------------------+
|  rtb-0c500fce31e3bf721                   |
+------------------------------------------+
||                 Routes                 ||
|+-----------------------+----------------+|
||         Dest          |    Target      ||
|+-----------------------+----------------+|
||  10.0.0.0/16          |  local         ||
|+-----------------------+----------------+|
~ $ 
