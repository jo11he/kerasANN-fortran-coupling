#! /bin/bash


if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS configuration
  echo $OSTYPE

  cd ./pythonANN
  python3 builder.py $OSTYPE
  install_name_tool -id "@loader_path/pythonANN/libplugin.dylib" libplugin.dylib

  cd ../
  gfortran -o run_test -L ./pythonANN/ -lplugin test_pythonANN.f90
  install_name_tool -change libplugin.dylib @loader_path/pythonANN/libplugin.dylib run_test
  install_name_tool -add_rpath @loader_path/pythonANN/ run_test


elif [[ "$OSTYPE" == *"linux"* ]]; then
  # linux configuration
  echo $OSTYPE

  module load python/3.6.7 # for tycho!
  cd ./pythonANN
  python3 builder.py $OSTYPE
  cd ../
  gfortran -o run_test -Wl,-rpath=./pythonANN/ -L ./pythonANN/ -lplugin test_pythonANN.f90


fi





