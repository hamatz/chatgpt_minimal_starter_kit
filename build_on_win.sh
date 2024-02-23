# install_preparation_for_windows.ps1 を実行して準備
.\install_preparation_for_win.ps1

Write-Host "Starting app build process with additional arguments: $args"
flet build $args

Write-Host "App build process completed."