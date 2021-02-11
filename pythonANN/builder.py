# builder.py
# run through make or prebuild.sh
# to run manually: python3 builder.py $OSTYPE $HOSTNAME

# extra compiling options
FFLAGS = [] # list of strings
# extra linking options, passed to ffibuilder.set_source -> see linux-tycho config (l.70)
# most notably required to link python libraries in non-standard locations
# set automatically on tycho host platform
LIBS = [] # list of strings

import sys
import cffi

ffibuilder = cffi.FFI()

if len(sys.argv) < 3: raise ValueError('missing input at position 1 ($OSTYPE) or 2 ($HOSTNAME)')
else: OS = sys.argv[1] ; HOST = sys.argv[2]



header = '''
extern void get_rates(double *, double *, double *, double *, double *, int32_t *, double *, double *, int32_t *);
'''

module = '''

import sys
if not hasattr(sys, 'argv'):
    sys.argv  = ['']
import numpy as np
# add local dir to load own modules 
sys.path.extend(['./pythonANN']) #(gearbox, prediction_pipe)
import gearbox
import prediction_pipe

from my_plugin import ffi

@ffi.def_extern()
def get_rates(x1_ptr, x2_ptr, x3_ptr, x4_ptr, x5_ptr, n_ptr, y1_ptr, y2_ptr, b_ptr):
    
    # gearbox in
    T_gas = gearbox.as_single(ffi, x1_ptr)
    nH = gearbox.as_single(ffi, x2_ptr) 
    n_H = gearbox.as_single(ffi, x3_ptr)
    n = gearbox.as_single(ffi, n_ptr)
    lam = gearbox.as_array(ffi, x4_ptr, shape=(n,))
    u = gearbox.as_array(ffi, x5_ptr, shape=(n,))
    b = gearbox.as_single(ffi, b_ptr)
    
    # call python main function
    if b == 1:
        LH, ER = prediction_pipe.make_prediction(T_gas, nH, n_H, lam, u, create_checkpoints=True)
    elif b == 0:
        LH, ER = prediction_pipe.make_prediction(T_gas, nH, n_H, lam, u, create_checkpoints=False)

    # gearbox out
    gearbox.get(LH, y1_ptr, 1, ffi)
    gearbox.get(ER, y2_ptr, 1, ffi)
    
'''

with open('plugin.h', 'w') as f:
    f.write(header)


if 'linux' in OS:

    if 'tycho' in HOST:
        print('building dynamic libs for tycho')

        ffibuilder.embedding_api(header)
        ffibuilder.set_source('my_plugin', r'''
                #include "plugin.h"
        ''',
                              extra_comile_args=FFLAGS,
                              extra_link_args=["-L/shared/apps/python/3.6.7/lib",
                                               "-Wl,-rpath=/shared/apps/python/3.6.7/lib",
                                               "-L/shared/apps/python/3.6.7/lib/python3.6/site-packages",
                                               "-Wl,-rpath=/shared/apps/python/3.6.7/lib/python3.6/site-packages",
                                               ]
                              )

    else:
        ffibuilder.embedding_api(header)
        ffibuilder.set_source('my_plugin', r'''
                    #include "plugin.h"
            ''',
                              extra_comile_args=FFLAGS,
                              extra_link_args=LIBS
                              )

    ffibuilder.embedding_init_code(module)
    ffibuilder.compile(target='libplugin.so', verbose=True)


elif 'darwin' in OS:

    print('building dynamic libs for macOS')
    ffibuilder.embedding_api(header)
    ffibuilder.set_source('my_plugin', r'''
                #include "plugin.h"
        ''',
                          extra_comile_args=FFLAGS,
                          extra_link_args=LIBS
                          )

    ffibuilder.embedding_init_code(module)
    ffibuilder.compile(target='libplugin.dylib', verbose=True)


