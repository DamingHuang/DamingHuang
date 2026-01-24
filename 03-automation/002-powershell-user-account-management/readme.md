# PowerShell Active Directory User Management

This repository contains PowerShell scripts to automate Active Directory (AD) user management operations. Create or remove multiple AD accounts using CSV files with minimal manual effort, featuring robust error handling, logging, and optional email notifications.

## 📋 Overview

These PowerShell scripts automate bulk Active Directory operations, originally inspired by [AttuneOps' User Account Management example](https://attuneops.io/powershell-automation-ideas-scripts/#User_Account_Management).
```powershell
#This script takes user data from a CSV file and generates new user accounts in Active Directory (AD) using that information.
 
Import-Csv "C:\path\to\users.csv" | ForEach-Object {

    New-ADUser -Name $_.Name -GivenName $_.FirstName -Surname $_.LastName -SamAccountName $_.Username -UserPrincipalName "$($_.Username)@domain.com" -Path "OU=Users,DC=domain,DC=com" -AccountPassword (ConvertTo-SecureString $_.Password -AsPlainText -Force) -Enabled $true

}

```
 I've expanded on that foundation to create production-ready tools with enhanced flexibility, error handling, and automation capabilities.


## ✨ Features

- **✅ Bulk User Creation** - Import users from CSV files
- **✅ Bulk User Removal** - Remove users from CSV files
- **✅ Email Notifications** - Send welcome emails to newly created users
- **✅ Group Management** - Add users to AD groups with validation
- **✅ Comprehensive Logging** - Transcript logging for all operations
- **✅ Error Handling & Reporting** - Detailed error reporting with continued processing
- **✅ Automation-Friendly** - No manual prompts required
- **✅ Optional Cleanup** - Automatic CSV cleanup after successful execution

## ⚙️ Prerequisites

- Windows PowerShell 5.1 or later
- Active Directory PowerShell module (RSAT: Active Directory feature)
- Administrative permissions in Active Directory
- Properly formatted CSV files (see Usage section)
- For email notifications: SMTP server access with credentials

## 📁 Scripts

### 1. `Create-ADUsers.ps1` - Basic User Creation
Simple script for bulk AD user creation from CSV.

**Required CSV columns:**
- `FirstName`
- `LastName`
- `Username`
- `Password`

### 2. `Remove-ADUsers.ps1` - Basic User Deletion
Simple script for bulk AD user removal from CSV.

**Required CSV columns:**
- `Username`

### 3. `errorhandling.ps1` - Advanced User Creation with Email Notifications
Enhanced user creation with error handling and email notifications.

**Features:**
- Email notification to newly created users
- Detailed error reporting
- User creation validation

**Required CSV columns:**
- `FirstName`
- `LastName`
- `Username`
- `Password`
- `Email`

### 4. `robustlogging.ps1` - Group Management with Logging
Add users to AD groups with comprehensive logging and validation.

**Features:**
- Transcript logging to file
- Group creation if not exists
- User validation before adding to groups

**Required CSV columns:**
- `Username`
- `GroupName`

## 🚀 Usage

### Basic User Creation
1. Prepare CSV with required columns
2. Update script paths and domain information:
   ```powershell
   # Update these variables:
   - CSV path: "your-path\file.csv"
   - Domain: "DC=yourdomain,DC=com"
   - OU path: "CN=Users,DC=yourdomain,DC=com"
