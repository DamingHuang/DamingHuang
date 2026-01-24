<#This script automates the creation of Active Directory (AD) users from a CSV file and optionally sends email notifications to the newly created users.
It includes error handling to ensure the script continues processing even if some operations fail.#>




 $scriptErrors = @()
$NewUsers = @()     # new users add to this array for later on purpose 
$catcherrors =@()
Import-Csv -Path "your path \file.csv " | ForEach-Object {


    New-ADUser `
        -Name $_.Name `
        -GivenName $_.FirstName `
        -Surname $_.LastName `
        -SamAccountName $_.Username `
        -UserPrincipalName "$($_.Username)@domain.com" `
        -Path "CN=Users,DC=CITYNEWYORKCOLLEGE,DC=com" `
        -AccountPassword (ConvertTo-SecureString $_.Password -AsPlainText -Force) `
        -Enabled $true `
        -ErrorAction SilentlyContinue `
        -ErrorVariable +scriptErrors

        $NewUsers += $_.Username
}



#check if csv in your array
$csv = Import-Csv -Path "C:\Users\Administrator\Desktop\csv\testusers.csv"

foreach ($row in $csv) {
    if ($row.Username -in $NewUsers) {
        Write-Host "$($row.Username) is IN the array." -ForegroundColor Green
        $From = "Admin@citycollegenewyork.com"
        $To = "$($row.Email)"
        $Subject = "Test Email"
        $Body = "This is a test email from PowerShell."
        $SMTPServer = "smtp.gmail.com"  # Replace with your company's SMTP server
        $SMTPPort = 587                # Usually 587 or 25
        $Username = "Email@gmail.com"
        $Password = "123 jzcn rzzx dytv rerh "
  
try {
    # 1. Add -ErrorAction Stop to force terminating errors into the catch block
    Send-MailMessage `
    -From $From `
    -To $To `
    -Subject $Subject `
    -Body $Body `
    -SmtpServer $SMTPServer `
    -Port $SMTPPort `
    -Credential (New-Object System.Management.Automation.PSCredential($Username,(ConvertTo-SecureString $Password -AsPlainText -Force))) `
    -UseSsl `
    -ErrorAction Stop
}

catch {
    # 2. Output the error details to the console

    ## You can output the entire error record for maximum detail:
    ##Write-Error "An error occurred while sending the email."
    $_ | Format-List -Force
    
    ## OR, for a cleaner, specific output:
    Write-Host "`n🚨 Email Sending Failed" -ForegroundColor Red
    Write-Host "---"
    Write-Host "Error Type: $($_.Exception.GetType().Name)" -ForegroundColor Yellow
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "Full Details: $($_.FullyQualifiedErrorId)" -ForegroundColor Yellow
    

}

        
  

    }
    else {
        Write-Host "$($row.Username) is NOT in the array." -ForegroundColor Red
    }
}




if ($scriptErrors.Count -gt 0) {
 
    Write-Host "The following errors were found:" -ForegroundColor Red
    $scriptErrors | ForEach-Object {
   




        Write-Host "-> $($_.Exception.Message)" $scriptErrors -ForegroundColor Red
       

    }
} else {
 
    Write-Host "All users from the CSV were processed successfully." -ForegroundColor Green
    Remove-Item  "your path\file.csv"
}




 
