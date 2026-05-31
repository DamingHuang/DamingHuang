$currentPath = pwd
$packages = @("pefile", "py7zr")

foreach ($package in $packages) {
    python -m pip show $package *> $null

    if ($LASTEXITCODE -ne 0) {
        Write-Host "$package is NOT installed. Installing..."
        python -m pip install $package
    }
    else {
        Write-Host "$package is already installed."
    }
}


 python scan.py $currentPath

