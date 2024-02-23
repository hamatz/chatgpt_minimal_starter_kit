# Prerequisites
# This code uses jp for parsing json file, so you need
# brew install jq
json_file='build_target_system_data.json'
assets_folder='./assets'

cat $json_file | jq -r '.folders[]' | while read folder; do
    echo "Copying folder: $folder to $assets_folder..."
    cp -r $folder $assets_folder/
done

cat $json_file | jq -r '.files[]' | while read file; do
    echo "Copying file: $file to $assets_folder..."
    cp $file $assets_folder/
done

echo "Completed copying system folders and files to $assets_folder."

