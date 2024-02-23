# install_preparation_for_windows.ps1 を実行して準備
.\install_preparation_for_win.ps1

$settingsFile = 'build_settings.json'

$jsonContent = Get-Content $settingsFile | ConvertFrom-Json
$buildVersion = $jsonContent.build_version
$buildNumber = $jsonContent.build_number
$projectName = $jsonContent.project_name
$moduleName = $jsonContent.module_name
$description = $jsonContent.description
$productName = $jsonContent.product_name
$orgName = $jsonContent.org_name
$companyName = $jsonContent.company_name
$copyright = $jsonContent.copyright

Write-Host "Starting app build process with additional arguments: $args"
flet build $args --build-version $buildVersion --build-number $buildNumber --project $projectName --description $description --product $productName --org $orgName --company $companyName --copyright $copyright --module-name $moduleName

Write-Host "App build process completed."