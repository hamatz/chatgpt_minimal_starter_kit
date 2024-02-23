#!/bin/bash
./install_preparation_for_mac.sh

# JSONファイルのパス
settings_file='build_settings.json'

# バージョン情報をJSONファイルから取得
build_version=$(cat $settings_file | jq -r '.build_version')
build_number=$(cat $settings_file | jq -r '.build_number')
project_name=$(cat $settings_file | jq -r '.project_name')
description=$(cat $settings_file | jq -r '.description')
product_name=$(cat $settings_file | jq -r '.product_name')
module_name=$(cat $settings_file | jq -r '.module_name')
org_name=$(cat $settings_file | jq -r '.org_name')
company_name=$(cat $settings_file | jq -r '.company_name')
copyright=$(cat $settings_file | jq -r '.copyright')

echo "Starting app build process with additional arguments: $@"
flet build $@ --build-version $build_version --build-number $build_number --project $project_name --description $description --product $product_name --org $org_name --company $company_name --copyright $copyright --module-name $module_name

echo "App build process completed."