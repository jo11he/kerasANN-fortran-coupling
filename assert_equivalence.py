import os
import numpy as np

checkpoint_path = './out/simX/ANN_checkpoints/'

gt_l = np.loadtxt('./pythonANN/test_data/lam_test.txt')[1:]
gt_u = np.loadtxt('./pythonANN/test_data/u_test.txt')[1:]

gt_T_gas = 4.113083490000000353e+01
gt_nH = 1.194153369999999995e+05
gt_n_H = 1.000000000000000000e+08

for checkpoint in [path for path in os.listdir(checkpoint_path) if os.path.isdir(os.path.join(checkpoint_path, path))]:
    checkpoint_path_i = os.path.join(checkpoint_path, checkpoint)

    load_rf = np.loadtxt(os.path.join(checkpoint_path_i, 'rf_spectrum.txt'))
    load_params = np.loadtxt(os.path.join(checkpoint_path_i, 'cloud_params.txt'))

    load_l = load_rf[:, 0]
    load_u = load_rf[:, 1]

    load_T_gas = load_params[0]
    load_nH = load_params[1]
    load_n_H = load_params[2]

    print('\n\n # # # # # # # # # # # # # # # # # \n\t ' + checkpoint + '\n # # # # # # # # # # # # # # # # #')

    # assert T
    #assert load_T_gas == gt_T_gas, 'T_gas not equivalent: '+ str(load_T_gas)+' vs '+str(gt_T_gas)
    print('delta on T: ', abs(load_T_gas-gt_T_gas))

    # assert nH
    #assert load_nH == gt_nH, 'n(H) not equivalent'
    print('delta on nH: ', abs(load_nH - gt_nH))
    # assert n_H
    #assert load_n_H == gt_n_H, 'n_H not equivalent'
    print('delta on n_H: ', abs(load_n_H - gt_n_H))

    # assert wavelength grid
    #assert np.alltrue(load_l == gt_l), 'wavelength grid not equivalent'
    abs_diff_l = abs(load_l - gt_l)
    max_diff_l = abs_diff_l[np.argmax(abs_diff_l)]
    print('max delta on grid: ', max_diff_l, 'at index ', np.argmax(abs_diff_l))

    # assert energy density
    #assert np.alltrue(load_u == gt_u), 'energy density not equivalent'
    abs_diff_u = abs(load_u - gt_u)
    max_diff_u = abs_diff_u[np.argmax(abs_diff_u)]
    print('max delta on u: ', max_diff_l, 'at index ', np.argmax(abs_diff_l))

    #print(' # # # # # # # # # # # # # # # # # \n\tpassed '+ checkpoint+ '\n # # # # # # # # # # # # # # # # #')