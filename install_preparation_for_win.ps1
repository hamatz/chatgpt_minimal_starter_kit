$jsonFile = 'build_target_system_data.json'
$assetsFolder = '.\assets'
$jsonContent = Get-Content $jsonFile | ConvertFrom-Json

foreach ($folder in $jsonContent.folders) {
    Write-Host "Copying folder: $folder to $assetsFolder..."
    Copy-Item -Path $folder -Destination $assetsFolder -Recurse -Force
}

foreach ($file in $jsonContent.files) {
    Write-Host "Copying file: $file to $assetsFolder..."
    Copy-Item -Path $file -Destination $assetsFolder -Force
}

Write-Host "Completed copying system folders and files to $assetsFolder."
