 
$import = Import-Csv 'your path\your.csv'
$logFile = "your path\your-log.txt"

$invalidUser = @()
$invlaidUser = @()
 


$wrapgroup = {

Start-Transcript -Path $logFile -Append


   $import | ForEach-Object {
    $groupName = $_.GroupName
    $username  = $_.Username

    try {
        $group = Get-ADGroup -Identity $groupName -ErrorAction Stop
        Write-Host "Group exists: $groupName" -ForegroundColor Green
        }

    catch {
        Write-Host "Creating group $groupName because it doesn't exist" -ForegroundColor Yellow
        New-ADGroup -Name $groupName -GroupScope Global -Path "CN=Users,DC=CityNewYorkCollege,DC=com" -ErrorAction Stop
     }

  try{
   
   $user= get-aduser -Identity  $username -ErrorAction    Stop
   Write-Host "User exists: $username" -ForegroundColor Green
        Add-ADGroupMember $groupName -Members $username -ErrorAction Stop
  }

  catch{
     Write-Host " $username   it doesn't exist" -ForegroundColor Yellow
     $invlaidUser  += $username
     }
   }


if ($addedtogroupMSG.Count -gt 0) {
    Write-Host "`n These are InvalidUsers please check with Admin   " -ForegroundColor Green
    $invlaidUser
}

Stop-Transcript

}

& $wrapgroup
