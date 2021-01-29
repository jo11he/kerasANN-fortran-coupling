
#########################################################################
# # # # # # # # # Transformation functions and wrapper # # # # # # # # #
#########################################################################

import numpy as np
import scipy as sc
import scipy.interpolate
import scipy.integrate


# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # defines intervals for sampling logic# # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #


def final_sampling_bands():   # = it3
    FUV = [911.7, 3000]
    IRE = [4e4, 3e5]

    smooth1 = [FUV[1], IRE[0]]
    smooth2 = [IRE[1], 5e6]
    smooth3 = [5e6, 1e9]

    return [FUV, smooth1, IRE, smooth2, smooth3]


# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # Formatting Function # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #


def merge_bands(lst, lst_in_list=False):

    # look for my dimension[1]
    widths = []
    for arr in lst:
        widths.append(arr.shape[1])
    max_width = max(np.array(widths))

    # first array, rest will be concatenated to it
    m_arr = lst[0]
    # ensure that it has dim[1] of max dim[1] by buffering with np.zeros array
    while m_arr.shape[1] != max_width:
        m_arr = np.concatenate((m_arr, np.zeros((m_arr.shape[0], 1))), axis=1)

    for band in lst[1:]:
        # lst_in_list depreciated
        if lst_in_list:
            m_arr = np.concatenate((m_arr, np.array(band)))
        else:
            # ensure that it has dim[1] of max dim[1] by buffering with np.zeros array
            while band.shape[1] != max_width:
                band = np.concatenate((band, np.zeros((band.shape[0], 1))), axis=1)
            # concatenate to collection
            m_arr = np.concatenate((m_arr, band))

    return m_arr


# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # Main Transformation Functionalities # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #

def downsample_band(x_band, y_band, n_sample, lin_bipart=False, manual=[]):

    def trapz_avg(y_split, Q_split, weighting=None):

        if len(Q_split) != 0:
            return 0.5 * np.average(y_split[:-1] * Q_split[:-1] + y_split[1:] * Q_split[1:], weights=weighting)

        else:
            return 0.5 * np.average(y_split[:-1] + y_split[1:], weights=weighting)

    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    # interpolate for log spacing within the band
    y_interpolator = sc.interpolate.interp1d(x_band, y_band)
    min_x = x_band[0]
    max_x = x_band[-1]
    x_band = np.logspace(np.log10(min_x), np.log10(max_x), x_band.shape[0], endpoint=False)
    x_band[0] = min_x # for stability of the interpolator range
    x_band[-1] = max_x # for stability of the interpolator range
    y_band = y_interpolator(x_band)

    if len(manual) != 0:

        central_ps = manual
        boundary_idxs = [find_nearest(x_band, (c_lower + c_upper) / 2)[1] for c_lower, c_upper in
                         zip(central_ps[:-1], central_ps[1:])]

        x_splits = np.array_split(x_band, boundary_idxs)
        y_splits = np.array_split(y_band, boundary_idxs)

    else:
        x_splits = np.array_split(x_band, n_sample)
        y_splits = np.array_split(y_band, n_sample)

    # - - - -
    if lin_bipart:
        TS_arr = np.zeros([n_sample, 3])  # TS is the fully transformed spectrum (incl Q info if kwarg is true)
    else:
        TS_arr = np.zeros([n_sample, 2])

    # S_p (defined later) is a spectrum (prime) that has the same transform such that T(S) = T(S')

    i_sam = 0

    for x_split, y_split in zip(x_splits, y_splits):

        x_diff = x_split[1:] - x_split[:-1]
        x_weights = x_diff / sum(x_diff)
        x_mean = np.average(x_split)

        if lin_bipart:
            S_avg = trapz_avg(y_split, [], weighting=x_weights)
            b = (np.log10(y_split[-1]) - np.log10(y_split[0])) / (np.log10(x_split[-1]) - np.log10(x_split[0]))
            C = S_avg * (x_split[-1] - x_split[0])
            a = C / sc.integrate.trapz(x_split ** b, x_split)
            TS_arr[i_sam, :] = [x_mean, a, b]
            # reconstruct equivalent
            S_p_xy = np.concatenate((x_split.reshape(-1, 1), a * x_split.reshape(-1, 1) ** b), axis=1)

        else:
            yTS = trapz_avg(y_split, [], weighting=x_weights)
            TS_arr[i_sam][:] = [x_mean, yTS]
            # reconstruct equivalent
            S_p_val = yTS
            S_p_xy = np.concatenate((x_split.reshape(-1, 1), S_p_val * np.ones(x_split.reshape(-1, 1).shape)), axis=1)

        if i_sam == 0:
            S_p_arr = S_p_xy
        else:
            S_p_arr = np.concatenate((S_p_arr, S_p_xy), axis=0)

        # important!
        i_sam = i_sam + 1

    return TS_arr, S_p_arr


# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# final touch to get TS into operational form

def skim_TS(data):
    coef1 = data[:, 1]
    coef2 = data[:, 2]
    nonzero_coef2 = coef2[abs(coef2) > 0]

    one_dim = np.concatenate((coef1.reshape(-1, 1), nonzero_coef2.reshape(-1, 1)), axis=0)
    return one_dim


# # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # Transformation Wrapper Function # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #


def transform_single_spectrum(S, s_per_b, bands=final_sampling_bands(), array_in=[], array_out=True, lin_bip_idx=[1],
                       manual_idx=[], manual=[]):
    TS_lst = []
    S_p_lst = []

    print(s_per_b)
    band_idx = 0

    for band, n_sample in zip(bands, s_per_b):

        if len(array_in) != 0:
            x_band = array_in.T[:][0]
            y_band = array_in.T[:][1]

        else:
            x_band = S[:, 0]
            y_band = S[:, 1]

        y_band = y_band[x_band >= band[0]]
        x_band = x_band[x_band >= band[0]]

        y_band = y_band[x_band < band[1]]
        x_band = x_band[x_band < band[1]]

        # take n_samples for this band then conduct partial transform

        if band_idx in lin_bip_idx:
            print('unweighted lin_by_part active in interval ', band_idx, band)
            TS_band, S_p_band = downsample_band(x_band, y_band, n_sample, lin_bipart=True, manual=[])

        elif band_idx in manual_idx:
            print('unweighted by part on manual points ', band_idx, band)
            n_sample = len(manual)
            TS_band, S_p_band = downsample_band(x_band, y_band, n_sample, lin_bipart=False, manual=manual)
        else:
            print('generic unweighted transformation in interval', band_idx, band)
            TS_band, S_p_band = downsample_band(x_band, y_band, n_sample, lin_bipart=False, manual=[])

        TS_lst.append(TS_band)
        S_p_lst.append(S_p_band)

        band_idx += 1

    if array_out:

        return merge_bands(TS_lst), merge_bands(S_p_lst)

    else:

        return TS_lst, S_p_lst
