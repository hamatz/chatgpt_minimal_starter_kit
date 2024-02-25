#!/bin/bash
# JSONファイルのパス
settings_file='build_settings.json'

# バージョン情報をJSONファイルから取得
product_version=$(cat $settings_file | jq -r '.product_version')
build_number=$(cat $settings_file | jq -r '.build_number')
product_name=$(cat $settings_file | jq -r '.product_name')
copyright=$(cat $settings_file | jq -r '.copyright')

copyfiles="system:system"
icon="work/cf_logo.png"

echo "Starting app pack process..."
flet pack --product-version $product_version --bundle-id $build_number --product-name $product_name  --copyright $copyright  --icon $icon --add-data=$copyfiles app.py

echo "App packaging process completed."