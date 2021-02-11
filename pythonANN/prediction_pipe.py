#prediciton_pipe.py

import os
import sys
import shutil
import time

print(sys.version)

# supress general warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
test_ID = 1

# supress tensorflow warnings
from tensorflow import compat
compat.v1.logging.set_verbosity(compat.v1.logging.ERROR)

import random
import numpy as np
from transform_tools import final_sampling_bands, transform_single_spectrum, skim_TS
from tensorflow.keras.models import load_model


# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # ESTABLISH STATE (SCALERS, MODELS) OF MODULE # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # IMPORTANT PATH VARIABLES # # # # # # #
path_to_scalers = './pythonANN/scalers'  # scalers usually shipped in this directory
path_to_models = './pythonANN/models' # models usually shipped in this directory

# # # # # LOADING SCALERS & MODELS # # # # # # # #
x_scaling_coeffs = np.loadtxt(os.path.join(path_to_scalers, 'x_scaling_coeffs.txt'))
y_scaling_coeffs = np.loadtxt(os.path.join(path_to_scalers, 'y_scaling_coeffs.txt'))
LH_model = load_model(os.path.join(path_to_models, 'LH_MODEL'))
ER_model = load_model(os.path.join(path_to_models, 'ER_MODEL'))

# # # # # # # DETECT AND SET CURRENT SIM OUT PATH # # # # # # # # #
out_dir = 'out'
out_subdirs = [os.path.join(out_dir, d) for d in os.listdir (out_dir)
               if os.path.isdir(os.path.join(out_dir, d))
               and d != 'check_ANN']
current_out = max(out_subdirs, key=os.path.getmtime)


# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # #            FUNCTION DEFINITIONS             # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #

#functional implementation of spectrum transformation
def single_spectrum_transform(S, bands=final_sampling_bands(), samples_per_band=[5, 3, 5, 6, 1],
                              lin_bip_idx=[1], manual_idx=[3], manual=[3.6e5, 4.8e5, 6e5, 8e5, 14.6e5, 32e5]):

    #verboseprint = print if verbose else lambda *a, **k: None

    #verboseprint('Transforming spectrum')
    TS, __ = transform_single_spectrum(S, samples_per_band, bands=bands, array_out=True,
                                          lin_bip_idx=lin_bip_idx, manual_idx=manual_idx, manual=manual)

    flat_TS = skim_TS(TS).flatten()

    return flat_TS


# function for (reverse) scaling of x_data and y_data when scaling coefficients exist already
# taken from LEGACY/B_datasets/DataSet_utils.py (Jan 29., commit 29e4f8932c5f0231d58797e510e7d488929859b8)
def fixed_coeff_scaler(data, coeffs, slopes_inds=[23, 24, 25], mode='to_unit', verbose=0):

    #verboseprint = print if verbose else lambda *a, **k: None

    if mode == 'to_unit':

        if data.shape[1] == coeffs.shape[0]:

            for col_ind in range(data.shape[1]):

                col_data = data[:, col_ind]

                if col_ind in slopes_inds:  # log space

                    a = coeffs[col_ind][0]
                    b = coeffs[col_ind][1]

                    scaled_col_data = (col_data + b) / a

                else:  # lin space

                    a = coeffs[col_ind][0]
                    b = coeffs[col_ind][1]

                    scaled_col_data = a * (np.log10(col_data) + b)

                if col_ind == 0:
                    scaled_data = scaled_col_data.reshape(-1, 1)
                else:
                    scaled_data = np.concatenate((scaled_data, scaled_col_data.reshape(-1, 1)), axis=1)

            #verboseprint('\ntest scaling:\n', np.amax(scaled_data, axis=0), '\n', np.amin(scaled_data, axis=0))

            return scaled_data

        else:
            print('Scaling coefficients do not match size of data to be scaled')


    elif mode == 'to_physical':

        if data.shape[1] == coeffs.shape[0]:

            for col_ind in range(data.shape[1]):

                col_data = data[:, col_ind]

                if col_ind in slopes_inds:  # log space

                    a = coeffs[col_ind][0]
                    b = coeffs[col_ind][1]

                    scaled_col_data = col_data * a - b

                else:  # lin space

                    a = coeffs[col_ind][0]
                    b = coeffs[col_ind][1]

                    scaled_col_data = 10 ** (col_data / a - b)

                if col_ind == 0:
                    scaled_data = scaled_col_data.reshape(-1, 1)
                else:
                    scaled_data = np.concatenate((scaled_data, scaled_col_data.reshape(-1, 1)), axis=1)

            return scaled_data

        else:
            print('Scaling coefficients do not match size of data to be scaled')

    else:
        print('invalid scaling mode')


# function taking individual input parameters, combining them to x_data_raw and scaling to scaled x_data for ANNs
def x_data_treatment(T_gas, nH, n_H, rf, x_scaler):

    # concatenate x data
    X = np.concatenate((np.array([T_gas]), np.array([nH]), np.array([n_H]), rf), axis=0).reshape(1, -1)

    # apply data scaler on x data
    x = fixed_coeff_scaler(X, x_scaler, slopes_inds=[23, 24, 25], mode='to_unit')
    return x


# main function:
def make_prediction(T_gas, nH, n_H, lam, u, create_checkpoints=False):

    # # # # # # # CAST ARRAYS INTO S # # # # # # #
    lam = lam.reshape(-1, 1)
    u = u.reshape(-1, 1)
    S = np.concatenate((lam, u), axis=1)

    # # # # # # # TRANSFORM SPECTRUM # # # # # # #
    rf = single_spectrum_transform(S)

    # # # # # INPUT DATA TREATMENT # # # # # # # #
    x = x_data_treatment(T_gas, nH, n_H, rf, x_scaling_coeffs)

    # # # # # MAKE PREDICTIONS # # # # # # #

    lh = LH_model.predict(x)
    er = ER_model.predict(x)
    y = np.array([lh, er]).reshape(1, -1)

    # # # SCALE BACK TO PHYSICAL UNITS # # #
    Y = fixed_coeff_scaler(y, y_scaling_coeffs, slopes_inds=[], mode='to_physical')[0]

    if create_checkpoints:
        # # # SAVE INPUTS, SPECTRUM AND COMPUTED RESULTS # # #
        chance = random.uniform(0, 1)
        if chance < 0.1:
            time1 = time.time()

            test_ID = 1
            save_path = os.path.join(current_out, 'ANN_checkpoints', 'checkpoint_'+str(test_ID))

            #set output directory
            while os.path.exists(save_path):
                test_ID = int(save_path.rsplit('checkpoint_', 1)[-1])+1
                save_path = save_path.rsplit('_', 1)[0] + '_' + str(test_ID)
            os.makedirs(save_path)

            with open(os.path.join(save_path, 'rf_spectrum.txt'), 'w') as lamu_file, \
                    open(os.path.join(save_path, 'cloud_params.txt'), 'w') as params_file, \
                    open(os.path.join(save_path, 'rate_coeffs.txt'), 'w') as result_file:

                lamu_file.write('# [0] lambda (nm), [1] u_lambda (erg.cm-3.A-1)\n')
                params_file.write('# [0] T_gas (K), [1] n(H) (cm-3), [2] n(H) (cm-3)\n')
                result_file.write('# [0] R_LH (cm3.s-1), [1] R_ER (cm3.s-1)\n')

                np.savetxt(lamu_file, S)
                np.savetxt(params_file, np.array([T_gas, nH, n_H]), newline=' ')
                np.savetxt(result_file, np.array([Y[0], Y[1]]), newline=' ')

                time2 = time.time()

                print('\n # # # # # # # # # # # # # # # # # # # # #  \n '
                      '\tCreated ANN Checkpoint #'+str(test_ID) + '\n' +
                      '\t   [ cost : ', round(time2 - time1, 3), ' s ]' +
                      '\n # # # # # # # # # # # # # # # # # # # # #  \n ')


        else:
            pass

    return Y[0], Y[1]
