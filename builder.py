import cffi

ffibuilder = cffi.FFI()

header = '''
extern void get_rates(double *, double *, double *, double *, double *, int32_t *, double *, double *);
'''

module = '''

import numpy as np

import sys
# add local dir to load own modules 
sys.path.extend(['.']) #(gearbox, prediction_pipe)
import gearbox
import prediction_pipe

from my_plugin import ffi

@ffi.def_extern()
def get_rates(x1_ptr, x2_ptr, x3_ptr, x4_ptr, x5_ptr, n_ptr, y1_ptr, y2_ptr):
    
    # gearbox in
    T_gas = gearbox.as_single(ffi, x1_ptr)
    nH = gearbox.as_single(ffi, x2_ptr) 
    n_H = gearbox.as_single(ffi, x3_ptr)
    n = gearbox.as_single(ffi, n_ptr)
    lam = gearbox.as_array(ffi, x4_ptr, shape=(n,))
    u = gearbox.as_array(ffi, x5_ptr, shape=(n,))
    
    #print('input received: T_gas:' , T_gas, '\t n(H):' , nH, '\t n_H:' , n_H, '\t rf: spectral shape', u.shape, '...')
    
    # call python main function
    LH, ER = prediction_pipe.make_prediction(T_gas, nH, n_H, lam, u)
    #print('Prediction results: ', LH, ER)
    
    # gearbox out
    gearbox.get(LH, y1_ptr, 1, ffi)
    gearbox.get(ER, y2_ptr, 1, ffi)
    
'''

with open('plugin.h', 'w') as f:
    f.write(header)

ffibuilder.embedding_api(header)
ffibuilder.set_source('my_plugin', r'''
        #include "plugin.h"
''')

ffibuilder.embedding_init_code(module)
ffibuilder.compile(target='libplugin.dylib', verbose=True)

### run build with 'python builder.py' ###