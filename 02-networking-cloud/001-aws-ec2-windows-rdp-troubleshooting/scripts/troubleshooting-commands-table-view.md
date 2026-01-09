#!/bin/bash
# AWS EC2 RDP Troubleshooting Commands
# Date: 2026-01-04
# Issue: RDP Error 0x204 - Private Subnet Access Problem

echo "=== AWS EC2 RDP Troubleshooting Commands ==="

# 1. Instance Details
echo "1. Checking instance details..."
aws ec2 describe-instances --instance-ids i-0e3229b9ac12f5a39 --output table

```bash
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

```
 
# 2. Security Group Rules
echo -e "\n2. Checking security group rules..."
aws ec2 describe-security-groups --group-ids sg-078968af2967efd66 --query 'SecurityGroups[*].{Name:GroupName, Ingress:IpPermissions[*].{Port:FromPort, Protocol:IpProtocol, Source:IpRanges[0].CidrIp}}' --output table

# 3. Route Tables
echo -e "\n3. Checking route tables..."
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=vpc-0517d5e295a732156" --query 'RouteTables[*].{ID:RouteTableId, Routes:Routes[*].{Dest:DestinationCidrBlock, Target:GatewayId}}' --output table

# 4. Subnet Details
echo -e "\n4. Checking subnet configuration..."
aws ec2 describe-subnets --subnet-ids subnet-048bc52084885ebae --query 'Subnets[*].{SubnetId:SubnetId, CIDR:CidrBlock, PublicIP:MapPublicIpOnLaunch, RouteTable:Tags[?Key==`Name`].Value|[0]}' --output table

# 5. Network Interface
echo -e "\n5. Checking network interface..."
aws ec2 describe-network-interfaces --network-interface-ids eni-091ab1a2df2d5d2e7 --query 'NetworkInterfaces[*].{PrivateIP:PrivateIpAddress, PublicIP:Association.PublicIp, Subnet:SubnetId}' --output table
