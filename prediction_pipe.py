#prediciton_pipe.py

import os
import numpy as np
from tensorflow.keras.models import load_model


# function for (reverse) scaling of x_data and y_data when scaling coefficients exist already
# taken from LEGACY/B_datasets/DataSet_utils.py (Jan 29., commit 29e4f8932c5f0231d58797e510e7d488929859b8)
def fixed_coeff_scaler(data, coeffs, slopes_inds=[23, 24, 25], mode='to_unit'):
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

            print('\ntest scaling:\n', np.amax(scaled_data, axis=0), '\n', np.amin(scaled_data, axis=0))

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
def make_prediction(T_gas, nH, n_H, rf):

    # # # # IMPORTANT PATH VARIABLES # # # # # # #
    path_to_scalers = './scalers'  # scalers usually shipped in this directory
    path_to_models = './models' # models usually shipped in this directory

    # # # # # LOADING DATA SCALERS # # # # # # # #
    x_scaling_coeffs = np.loadtxt(os.path.join(path_to_scalers, 'x_scaling_coeffs.txt'))
    y_scaling_coeffs = np.loadtxt(os.path.join(path_to_scalers, 'y_scaling_coeffs.txt'))

    # # # # # INPUT DATA TREATMENT # # # # # # # #
    x = x_data_treatment(T_gas, nH, n_H, rf, x_scaling_coeffs)

    # # # # # LOADING MODELS # # # # # # # #
    LH_model = load_model(os.path.join(path_to_models, 'LH_MODEL'))
    ER_model = load_model(os.path.join(path_to_models, 'ER_MODEL'))

    # # # # # MAKE PREDICTIONS # # # # # # #
    lh = LH_model.predict(x)
    er = ER_model.predict(x)
    y = np.array([lh, er]).reshape(1, -1)

    # # # SCALE BACK TO PHYSICAL UNITS # # #
    Y = fixed_coeff_scaler(y, y_scaling_coeffs, slopes_inds=[], mode='to_physical')[0]

    return Y[0], Y[1]









    y_scaling_coeffs = np.loadtxt(os.path.join(path_to_coeffs, 'y_scaling_coeffs.txt'))
