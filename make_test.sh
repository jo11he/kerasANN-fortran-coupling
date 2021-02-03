#! /bin/bash

# macOS configuration

cd ./pythonANN
python builder.py
install_name_tool -id "@loader_path/pythonANN/libplugin.dylib" libplugin.dylib

cd ../
gfortran -o run_test -L ./pythonANN/ -lplugin test_pythonANN.f90
install_name_tool -change libplugin.dylib @loader_path/pythonANN/libplugin.dylib run_test
install_name_tool -add_rpath @loader_path/pythonANN/ run_test

## linux configuration
#cd ./pythonANN
#python builder.py
#cd ../
#gfortran -o run_test -Wl,-rpath=./pythonANN/ -L ./pythonANN/ -lplugin test_pythonANN.f90