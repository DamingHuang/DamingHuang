# PowerShell AD User Management
This repository contains PowerShell scripts to automate Active Directory (AD) user management. Create or remove multiple AD accounts using CSV files with minimal manual effort.

## Overview
This PowerShell script automates the bulk creation of Active Directory (AD) user accounts by importing data from a CSV file. 

It was originally inspired by [AttuneOps' User Account Management example](https://attuneops.io/powershell-automation-ideas-scripts/#User_Account_Management), which demonstrated using `Import-Csv` with `New-ADUser`.  
I expanded on that foundation to make the script more flexible, robust, and production-friendly
## Features
- ✅ Bulk User Creation from CSV
- ✅ Bulk User Removal from CSV
- ✅ Error Handling & Reporting
- ✅ Automation-Friendly (no manual prompts)
- ✅ Optional CSV cleanup after execution
## Prerequisites
- Windows PowerShell (5.1 or later)
- Active Directory module for PowerShell (`RSAT: Active Directory` feature installed)
- Administrative permissions in AD
- CSV files formatted correctly for either user creation or deletion
## Usage

### 1. Create Users
1. Prepare a CSV file with columns: `FirstName, LastName, Username, Password`
2. Update the path in `Create-ADUsers.ps1`:
3. Run the script
