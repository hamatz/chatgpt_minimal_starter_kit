$settingsFile = 'build_settings.json'

$jsonContent = Get-Content $settingsFile | ConvertFrom-Json
$buildVersion = $jsonContent.product_version
$buildNumber = $jsonContent.build_number
$description = $jsonContent.description
$productName = $jsonContent.product_name
$copyright = $jsonContent.copyright

Write-Host "Starting app packaging process"
flet pack --build-version $buildVersion --build-number $buildNumber --description $description --product $productName --copyright $copyright --add-data="system;system" app.py

Write-Host "App packaging process completed."