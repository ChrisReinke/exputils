import exputils as eu
import numpy as np


def test_dict_equal():

    dict1 = dict(x=4)
    dict2 = dict(x=4)
    assert eu.misc.dict_equal(dict1, dict2)

    dict1 = dict(x=4)
    dict2 = dict(x=3)
    assert not eu.misc.dict_equal(dict1, dict2)

    # different types
    dict1 = dict(x=4)
    dict2 = 'd'
    assert not eu.misc.dict_equal(dict1, dict2)


def test_numpy_vstack_2d_default():

    mat1 = [1, 2, 3, 4]
    mat2 = [10, 20, 30, 40]

    result = eu.misc.numpy_vstack_2d_default(mat1, mat2)

    trg = np.array([[1, 2, 3, 4], [10, 20, 30, 40]])

    assert np.all(result == trg)


    #################

    mat1 = [1, 2, 3]
    mat2 = [10, 20, 30, 40]

    result = eu.misc.numpy_vstack_2d_default(mat1, mat2)

    trg = np.array([[1, 2, 3, np.nan], [10, 20, 30, 40]])

    np.testing.assert_equal(result, trg)


    #################

    mat1 = [1, 2, 3, 4]
    mat2 = [10, 20, 30]

    result = eu.misc.numpy_vstack_2d_default(mat1, mat2)

    trg = np.array([[1, 2, 3, 4], [10, 20, 30, np.nan]])

    np.testing.assert_equal(result, trg)


    #################

    mat1 = [[1, 2, 3, 4], [5, 6, 7, 8]]
    mat2 = [10, 20, 30]

    result = eu.misc.numpy_vstack_2d_default(mat1, mat2)

    trg = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [10, 20, 30, np.nan]])

    np.testing.assert_equal(result, trg)


    #################

    mat1 = []
    mat2 = [10, 20, 30]

    result = eu.misc.numpy_vstack_2d_default(mat1, mat2)

    trg = np.array([10, 20, 30])

    np.testing.assert_equal(result, trg)


def test_boolean_filtering():

    # create data to filter:
    data = [dict(x=2, y=2),
            dict(x=2, y=3),
            dict(x=3, y=2),
            ]

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('x', '>', 4))
    assert np.all(np.array([False, False, False]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('y', '>=', 3))
    assert np.all(np.array([False, True, False]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('x', '<', 3))
    assert np.all(np.array([True, True, False]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('x', '<=', 2))
    assert np.all(np.array([True, True, False]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('x', '==', 2))
    assert np.all(np.array([True, True, False]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('x', '==', 'y'))
    assert np.all(np.array([True, False, False]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('x', '!=', 'y'))
    assert np.all(np.array([False, True, True]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, (('x', '<', 3) , 'and', ('y', '==', 3)))
    assert np.all(np.array([False, True, False]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, (('x', '==', 3) , 'or', ('y', '==', 3)))
    assert np.all(np.array([False, True, True]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, (('cumsum', 'x'), '==', 4 ))
    assert np.all(np.array([False, True, False]) == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('sum', 'x'))
    assert np.all(7 == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('max', 'x'))
    assert np.all(3 == filtered)

    filtered = eu.misc.do_subdict_boolean_filtering(data, ('min', 'x'))
    assert np.all(2 == filtered)


def test_list_equal():

    assert eu.misc.list_equal([1,2,3], [1,2,3])
    assert not eu.misc.list_equal([1, 2, 3], [1, 2, 3, 4])

    assert eu.misc.list_equal([1, [2, 2], 3], [1, [2, 2], 3])
    assert not eu.misc.list_equal([1, [2, 2], 3], [1, [2, 1], 3])

    assert eu.misc.list_equal([1, np.array([2, 2]), 3], [1, np.array([2, 2]), 3])
    assert not eu.misc.list_equal([1, np.array([2, 2]), 3], [1, np.array([2, 1]), 3])


def test_get_sub_dictionary_variable():

    test_dict = dict(var_a = 1,
                     sub_dict_1 = dict(
                         var_b = 2,
                         sub_dict_2 = dict(
                             var_c = [3, 4, 5],
                             var_c_multi = [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
                            )
                        ),
                     sub_list = [dict(var_d=6), dict(var_d=7)]
                     )

    var = eu.misc.get_dict_variable(test_dict, 'var_a')
    assert var == test_dict['var_a']

    var = eu.misc.get_dict_variable(test_dict, 'sub_dict_1.var_b')
    assert var == test_dict['sub_dict_1']['var_b']

    var = eu.misc.get_dict_variable(test_dict, 'sub_dict_1.sub_dict_2.var_c')
    assert var == test_dict['sub_dict_1']['sub_dict_2']['var_c']

    var = eu.misc.get_dict_variable(test_dict, 'sub_dict_1.sub_dict_2.var_c[1]')
    assert var == test_dict['sub_dict_1']['sub_dict_2']['var_c'][1]

    var = eu.misc.get_dict_variable(test_dict, 'sub_dict_1.sub_dict_2.var_c[-1]')
    assert var == test_dict['sub_dict_1']['sub_dict_2']['var_c'][-1]

    var = eu.misc.get_dict_variable(test_dict, 'sub_list[0].var_d')
    assert var == test_dict['sub_list'][0]['var_d']

    # slices:
    var = eu.misc.get_dict_variable(test_dict, 'sub_dict_1.sub_dict_2.var_c[:]')
    assert var == test_dict['sub_dict_1']['sub_dict_2']['var_c'][:]

    var = eu.misc.get_dict_variable(test_dict, 'sub_dict_1.sub_dict_2.var_c_multi[0,:]')
    assert var == test_dict['sub_dict_1']['sub_dict_2']['var_c_multi'][0][:]

    # key error for non existsing fields
    try:
        var = eu.misc.get_dict_variable(test_dict, 'sub_list[0].var_not_exists')
    except KeyError:
        pass

    # IndexError for non existsing fields
    try:
        var = eu.misc.get_dict_variable(test_dict, 'sub_dict_1.sub_dict_2.var_c[1000]')
    except IndexError:
        pass

    # IndexError for non existsing fields
    try:
        var = eu.misc.get_dict_variable(test_dict, 'sub_list[1000].var_d')
    except IndexError:
        pass

    # IndexError for wrong indexs
    try:
        var = eu.misc.get_dict_variable(test_dict, 'sub_dict_1.sub_dict_2.var_c_multi[1000]')
    except IndexError:
        pass



def test_str_to_slices():

    assert eu.misc.str_to_slices('[0]') == [0]
    assert eu.misc.str_to_slices('[0, 1]') == [0, 1]
    assert eu.misc.str_to_slices('[-1, 1]') == [-1, 1]
    assert eu.misc.str_to_slices('[-2, 1]') == [-2, 1]
    assert eu.misc.str_to_slices('[:, 1]') == [slice(None), 1]
    assert eu.misc.str_to_slices('[:, 1:]') == [slice(None), slice(1, None)]
    assert eu.misc.str_to_slices('[:, 1:4]') == [slice(None), slice(1, 4)]
    assert eu.misc.str_to_slices('[:, 1:10:2]') == [slice(None), slice(1, 10, 2)]
    assert eu.misc.str_to_slices('[[1,2]]') == [[1,2]]
    assert eu.misc.str_to_slices('[:, [1,2]]') == [slice(None), [1, 2]]