import exputils as eu
import numpy as np

def test_attrdict():

    attrdict = eu.AttrDict()
    attrdict['a'] = 1
    attrdict.b = 2

    assert attrdict.a == 1
    assert attrdict['a'] == 1

    assert attrdict.b == 2
    assert attrdict['b'] == 2


def test_attrdict_json_conversion():

    attrdict = eu.AttrDict()
    attrdict.nparray = np.array([1,2,3])
    attrdict.scalar = 2.0
    attrdict.subdict = eu.AttrDict()
    attrdict.subdict.scalar = 3.0

    # save as json
    json_data = attrdict.to_json()

    # load from json
    loaded_attrdict = eu.AttrDict.from_json(json_data)

    assert loaded_attrdict == attrdict

    ####################################
    # dict with integers as keys:
    attrdict = eu.AttrDict()
    attrdict[0] = 'hello'
    attrdict[1] = 'you'

    # save as json
    json_data = attrdict.to_json()

    # load from json
    loaded_attrdict = eu.AttrDict.from_json(json_data)

    assert loaded_attrdict == attrdict



def test_json_file(tmp_path):

    attrdict = eu.AttrDict()
    attrdict.nparray = np.array([1,2,3])
    attrdict.scalar = 2.0
    attrdict.subdict = eu.AttrDict()
    attrdict.subdict.scalar = 3.0

    attrdict.to_json_file(tmp_path / 'json_file')

    loaded_attrdict = eu.AttrDict.from_json_file(tmp_path / 'json_file')

    assert loaded_attrdict == attrdict


def test_combine_dicts():

    # simple dict
    def_dict = {'a': 1, 'b': 2}
    trg_dict = {'b': 20, 'c': 30}
    test_dict = {'a': 1, 'b': 20, 'c': 30}

    new_dict = eu.combine_dicts(trg_dict, def_dict)

    assert new_dict == test_dict


    # recursive dic
    def_dict = {'a': 1, 'b': {'aa': 5, 'bb': 6}}
    trg_dict = {'b': {'bb': 60, 'cc': 70}, 'c': 30}
    test_dict = {'a': 1, 'b': {'aa': 5, 'bb': 60, 'cc': 70}, 'c': 30}

    new_dict = eu.combine_dicts(trg_dict, def_dict)

    assert new_dict == test_dict

    # non-recursive
    def_dict = {'a': 1, 'b': {'aa': 5, 'bb': 6}}
    trg_dict = {'b': {'bb': 60, 'cc': 70}, 'c': 30}
    test_dict = {'a': 1, 'b': {'bb': 60, 'cc': 70}, 'c': 30}

    new_dict = eu.combine_dicts(trg_dict, def_dict, is_recursive=False)

    assert new_dict == test_dict

    # empty dict
    def_dict = {'a': 1, 'b': {'aa': 5, 'bb': 6}}
    trg_dict = None

    new_dict = eu.combine_dicts(trg_dict, def_dict)

    assert new_dict == def_dict


    # dict with function handles
    def_dict = eu.AttrDict({'a': eu.combine_dicts})
    trg_dict = None

    new_dict = eu.combine_dicts(trg_dict, def_dict)

    assert new_dict == def_dict

