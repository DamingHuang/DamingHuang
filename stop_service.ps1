$serviceNames = @("wuauserv", "WaaSMedicSvc", "usosvc")
$services = Get-Service -Name $serviceNames

foreach ($s in $services) {
    if ($s.Status -eq 'Running') {
        net stop $s.Name
    }
}
