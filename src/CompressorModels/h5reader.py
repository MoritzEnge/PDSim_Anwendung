import numpy as np
import h5py
import pandas as pd
from h5py import File, Group, Dataset
from pathlib import Path
from copy import deepcopy

def import_h5_as_dict(h5_FilePath, depth=1):
    res = {}
    res_nested = {}
    layers_keys = range(depth + 1)
    layers = dict.fromkeys(layers_keys, [])

    with h5py.File(h5_FilePath, 'r') as hdf:
        layers[0] = list(hdf.keys())
        new_layers = {0: layers[0].copy()}
        for i in range(depth):
            if not layers[i]:
                break
            else:
                if not i + 1 in new_layers:
                    new_layers.update({i + 1: []})
                for key in layers[i]:
                    # if key == 'FlowsProcessed':
                    #     print('FlowsProcessed')
                    # if key == 'FlowsProcessed/summed_mdot':
                    #     print('FlowsProcessed/summed_mdot')
                    if _key_is_dataset(hdf, key):
                        # if key == 'backend':
                        #     print('backend')
                        data = _read_data(hdf, key)
                        res.update({key: data})
                        res_nested = _include_key(res_nested, key)
                        res_nested = _add_data(res_nested, key, data)
                    else:
                        new_layers[i].remove(key)
                        keys_next_layer = list(hdf.get(key))
                        list_next_layer = []
                        for key_next_layer in keys_next_layer:
                            list_next_layer.append('{}/{}'.format(key, key_next_layer))
                        new_layers[i + 1].extend(list_next_layer)
            layers = deepcopy(new_layers)

    return layers, res, res_nested


def _key_is_dataset(h5py_File: File, key: str):
    if type(h5py_File.get(key)) == Dataset:
        return True
    return False


def _read_data(h5py_File: File, key: str):
    data = h5py_File.get(key)
    if isinstance(data, Group):
        data = list(data)
    elif isinstance(data, Dataset):
        data = data[()]
        if isinstance(data, bytes):
            # data = str(h5py_File.get(key)[()], encoding='utf-8')
            data = str(data, encoding='utf-8')
    return data


def _include_key(dict1: dict, long_key: str):
    key_list = long_key.split('/')
    dict2 = dict1.copy()

    if len(key_list) >= 1:
        if not key_list[0] in dict2.keys():
            dict2.update({key_list[0]: {}})
    if len(key_list) >= 2:
        if not key_list[1] in dict2[key_list[0]].keys():
            dict2[key_list[0]].update({key_list[1]: {}})
    if len(key_list) >= 3:
        if not key_list[2] in dict2[key_list[0]][key_list[1]].keys():
            dict2[key_list[0]][key_list[1]].update({key_list[2]: {}})
    if len(key_list) >= 4:
        if not key_list[3] in dict2[key_list[0]][key_list[1]][key_list[2]].keys():
            dict2[key_list[0]][key_list[1]][key_list[2]].update({key_list[3]: {}})
    if len(key_list) >= 5:
        if not key_list[4] in dict2[key_list[0]][key_list[1]][key_list[2]][key_list[3]].keys():
            dict2[key_list[0]][key_list[1]][key_list[2]][key_list[3]].update({key_list[4]: {}})
    if len(key_list) >= 6:
        if not key_list[5] in dict2[key_list[0]][key_list[1]][key_list[2]][key_list[3]][key_list[4]].keys():
            dict2[key_list[0]][key_list[1]][key_list[2]][key_list[3]][key_list[4]].update({key_list[5]: {}})
    if len(key_list) >= 7:
        print('layer is too deep')
    return dict2


def _add_data(dict1: dict, long_key: str, data):
    key_list = long_key.split('/')
    dict2 = dict1.copy()

    if len(key_list) == 1:
        dict2[long_key] = data
    elif len(key_list) == 2:
        dict2[key_list[0]][key_list[1]] = data
    elif len(key_list) == 3:
        dict2[key_list[0]][key_list[1]][key_list[2]] = data
    elif len(key_list) == 4:
        dict2[key_list[0]][key_list[1]][key_list[2]][key_list[3]] = data
    elif len(key_list) == 5:
        dict2[key_list[0]][key_list[1]][key_list[2]][key_list[3]][key_list[4]] = data
    elif len(key_list) == 6:
        dict2[key_list[0]][key_list[1]][key_list[2]][key_list[3]][key_list[4]][key_list[5]] = data

    return dict2


def get_h5file(h5_FilePath: Path):
    return h5py.File(str(h5_FilePath), 'r')


