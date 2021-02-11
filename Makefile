#============================================================================#
#============================================================================#
#                               CONFIGURATION                                #
#                                                                            #
#     1 - Set the name of your Fortran 90 compiler - variable FC             #
#     2 - Set the compilation options (variable FFLAGS)                      #
#     3 - If required, set the PATH and names of libraries :                 #
#         - LAPACK   in variable LIBS1                                       #
#         - BLAS     in variable LIBS1                                       #
#         Example :                                                          #
#         LIBS1 = -L/home/mypath_to_libraries -llapack -lblas                #
#                                                                            #
#         If the libraries are in standard directories, the "-L" option      #
#         is not necessary.                                                  #
#                                                                            #
#     On Mac, VecLib/Accelerate library can be used instead of LAPACK / BLAS #
#     To use the optimized Lapack on a Mac do not specify LIBS1              #
#     Replace at the end of the Makefile lines as :                          #
#     $(FC) $(FFLAGS) PXDR.o $(OBJstv) $(LIBS1) -o PDR                       #
#     by :                                                                   #
#     $(FC) $(FFLAGS) PXDR.o $(OBJstv) -Wl,-framework -Wl,Accelerate -o PDR  #
#     Do the same for PREP and CHEM_ANALYSER                                 #
#============================================================================#

SNAME := $(findstring Linux, $(shell uname -s))

#============================================================================#
#                                  GFORTRAN                                  #
#============================================================================#
  FC = gfortran

ifeq ($(SNAME), Linux)
$(info Using compilation options for Linux...)
  LIBS = -Wl,-rpath=./pythonANN/ -L./pythonANN/ -lplugin -L/shared/apps/python/3.6.7/lib -Wl,-rpath=/shared/apps/python/3.6.7/lib
else # MacOS ?
$(info Using compilation options for MacOS...)
  LIBS = -L ./pythonANN/ -lplugin
endif


.MAKEOPTS: -k -s




ALL: RUN_TEST
	echo "Compilation finished"


RUN_TEST:

#--- PREBUILD ANN MODULE ---------------------------------------------------------------
	./prebuild.sh
#--- Compile the TEST code ---------------------------------------------------------------
	$(FC) $(FFLAGS) test_pythonANN.f90 $(LIBS) -o RUN_TEST


# set paths for runtime linking of dynamic library (pythonANN)
ifeq ($(SNAME), Linux)
	echo "@rpath linked in compile"

else # MacOS ?
	echo "using install_name_tool for linking of dylib"
	install_name_tool -change libplugin.dylib @loader_path/pythonANN/libplugin.dylib RUN_TEST
	install_name_tool -add_rpath @loader_path/pythonANN/ RUN_TEST
endif

clean:
	\rm -f -r RUN_TEST ./pythonANN/*plugin*

