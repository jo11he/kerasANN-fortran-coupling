#! /bin/bash


if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS configuration
  echo 'Prebuilding pyANN module for' $OSTYPE

  cd ./pythonANN
  python3 builder.py $OSTYPE $HOSTNAME
  install_name_tool -id "@loader_path/pythonANN/libplugin.dylib" libplugin.dylib
  cd ../

elif [[ "$OSTYPE" == *"linux"* ]]; then
  # linux configuration
  echo $OSTYPE

  # module load python/3.6.7 # does not seem to work in sh
  cd ./pythonANN
  python3 builder.py $OSTYPE $HOSTNAME
  cd ../
fi





