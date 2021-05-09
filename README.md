Structured, quiet and high-performance example of kerasANN-f90 integration.
I used this as an environment to develop the ANN-f90 coupling before integration with the global .f90 simulation.


The interface between pythonANN and f90 global simulation is as follows:

State variables (local gas cloud conditions + high-dimensional radiation field spectrum) are passed from .f90 simulation to pythonANN, but remain unchanged. They only serve as an input to the prediction problem, which returns two new variables (H2 formation rates) to the .f90 global simulation.

Environment structure:

- test_pythonANN.f90, imitating the global .f90 simulation, containing the cbind interface definition on the .f90 side
- test_data directory, containing the rf spectrum state variables that are loaded into test_pythonANN.f90 (too large to hardcode into test_pythonANN.f90 like other state variables)
- pythonANN directory
    - prediction_pipe.py, transform_tools.py containing all functionality for the data conversion and ANN prediction problem, loading the ANN models and data scalers from the respective subdirectories 
    - gearbox.py containing all the conversion functions between python to C types
    - builder.py containing the static signature and definition of the shared function 'get_rates()' and the cffi command to build to shared library 'libplugin'
		


Run Coupling Test:

1. Compile TEST code via Makefile, entails two steps:
    - Makefile is executing "prebuild.sh", which will facilitate building shared library via builder.py.
        --> results in  .c, .o, .h files and the shared library 'libplugin', all contained within the "pythonANN" directory (design decision for tidiness of .f90 source code, at cost of complicated \\ linking procedure
    - Makefile makes executable for TEST code and link the shared library via LIBS argument \\
        --> results in RUN_TEST executable for running the test
    
2. Run Test Code ./RUN_TEST


Output:

The test_pythonANN.f90 simulates the global .f90 simulation, in which the ANN is called via the shared function get_rates() in a for loop (simulating local iterations, n=100).
The get_rates() function is fed the same inputs (state variables) from .f90 again and again, so all ANN outputs are identical. The time for each call of the shared function is measured.
The first call takes substantially longer than the subsequent calls, since it sets the state of the "prediction_pipeline.py" module which includes loading of the ANN and scaler objects.

The implementation contains an added feature which is the creation of so called "ANN checkpoints". When this functionality is toggled on (via the b_checkpoints variable in the .f90) each call to the get_rates() function has a non-zero probability of saving the input and output of the ANN to an external file under "out/simX/" (cost of this process is also monitored). The checkpoints can be used to evaluate the prediction accuracy of the ANN a-posteriori.



 - - - - - - - - - - - - 

Dependencies: 

Python 3
- os
- sys
- cffi
- numpy
- scipy
- tensorflow
- tensorflow.keras
