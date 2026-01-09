#!/bin/bash
# AWS EC2 RDP Troubleshooting Commands
# Date: 2026-01-04
# Issue: RDP Error 0x204 - Private Subnet Access Problem

echo "=== AWS EC2 RDP Troubleshooting Commands ==="

# 1. Instance Details
echo "1. Checking instance details..."
aws ec2 describe-instances --instance-ids i-0e3229b9ac12f5a39 --output table

```powershell
# Run as Administrator
Confirm-SecureBootUEFI

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
