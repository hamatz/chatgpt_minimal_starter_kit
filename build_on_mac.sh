#!/bin/bash
./install_preparation_for_mac.sh

echo "Starting app build process with additional arguments: $@"
flet build $@

echo "App build process completed."