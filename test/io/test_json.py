import exputils as eu
import numpy as np

def test_json_file(tmp_path):

    mydict = dict(
        nparray = np.array([1, 2, 3]),
        scalar = 2.0,
        subdict = dict(scalar = 3.0))

    # save the dict
    eu.io.save_dict_as_json_file(mydict, tmp_path / 'json_file')

    # save the dict
    loaded_dict = eu.io.load_dict_from_json_file(tmp_path / 'json_file')

    assert eu.misc.dict_equal(loaded_dict, mydict)

    #################################
    # check conversion of ints
    mydict = {1: {1: 'bla', 2: {'blubb': 0}},
              2: {1: 'bla', 2: {'s': 0}}}

    eu.io.save_dict_as_json_file(mydict, tmp_path / 'json_file')
    loaded_dict = eu.io.load_dict_from_json_file(tmp_path / 'json_file', is_transform_ints=True)
    assert eu.misc.dict_equal(loaded_dict, mydict)


def test_save_functions(tmp_path):

    mydict = dict(
        system_func = max,
        exputil_func = eu.misc.dict_equal,
        lambda_func = lambda x: x)

    # save the dict
    eu.io.save_dict_as_json_file(mydict, tmp_path / 'json_file')

    # save the dict
    loaded_dict = eu.io.load_dict_from_json_file(tmp_path / 'json_file')

    assert mydict['system_func'](1,2) == loaded_dict['system_func'](1,2)
    assert mydict['exputil_func']({}, {}) == loaded_dict['exputil_func']({}, {})
    assert mydict['lambda_func'](1) == loaded_dict['lambda_func'](1)

