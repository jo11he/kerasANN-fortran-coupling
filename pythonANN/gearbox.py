# gearbox.py
# modelled after: https://www.noahbrenowitz.com/post/calling-fortran-from-python/

import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
### ###  Create the dictionary mapping ctypes to np dtypes. ### ###
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

ctype2dtype = {}

# Integer types
for prefix in ('int', 'uint'):
    for log_bytes in range(4):
        ctype = '%s%d_t' % (prefix, 8 * (2**log_bytes))
        dtype = '%s%d' % (prefix[0], 2**log_bytes)

        ctype2dtype[ctype] = np.dtype(dtype)

# Floating point types
ctype2dtype['float'] = np.dtype('f4')
ctype2dtype['double'] = np.dtype('f8')



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
### ### ### ###    Cross-language communications    ### ### ### ###
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# wrap pointer in np.array and return full array
def as_array(ffi, ptr, shape, **kwargs):

    length = np.prod(shape)
    # Get the canonical C type of the elements of ptr as a string.
    T = ffi.getctype(ffi.typeof(ptr).item)

    if T not in ctype2dtype:
        raise RuntimeError("Cannot create array from element type: %s" % T)

    a = np.frombuffer(ffi.buffer(ptr, length * ffi.sizeof(T)), ctype2dtype[T]).reshape(shape, **kwargs)
    return a


# wrap pointer in np.array of fixed shape (1,) and return single value
def as_single(ffi, ptr, **kwargs):
    shape = (1,)
    length = 1
    T = ffi.getctype(ffi.typeof(ptr).item)

    if T not in ctype2dtype:
        raise RuntimeError("Cannot create array from element type: %s" % T)

    a = np.frombuffer(ffi.buffer(ptr, length * ffi.sizeof(T)), ctype2dtype[T]).reshape(shape, **kwargs)
    return a[0]


# get value via a numpy-wrapped c_pointer
def get(val, c_ptr, shape, ffi):

    # wrap pointer in numpy array
    fortran_arr = as_array(ffi, c_ptr, shape)

    # update the numpy array
    fortran_arr[:] = val





