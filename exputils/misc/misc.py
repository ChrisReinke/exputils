import numpy as np


def numpy_vstack_2d_default(array1, array2, default_value=np.nan):

    if len(array1) == 0:
        return array2

    if len(array2) == 0:
        return array1

    if np.ndim(array1) == 1:
        array1 = np.reshape(array1, (1,len(array1)))

    if np.ndim(array2) == 1:
        array2 = np.reshape(array2, (1,len(array2)))

    shape1 = np.shape(array1)
    shape2 = np.shape(array2)

    if shape1[1] == shape2[1]:
        return np.vstack((array1, array2))

    elif shape1[1] > shape2[1]:
        # add default values to array1

        new_values = np.ones((shape2[0], shape1[1] - shape2[1]))
        new_values[:] = default_value

        return np.vstack((array1, np.hstack((array2, new_values))))

    else:
        # add default values to array2

        new_values = np.ones((shape1[0], shape2[1] - shape1[1]))
        new_values[:] = default_value

        return np.vstack((np.hstack((array1, new_values)), array2))



def dict_equal(dict1, dict2):
        '''Checks if two dictionaries are equal. Allows to check numpy arrays as content.'''

        if not isinstance(dict1, dict) and not isinstance(dict2, dict):
            return dict1 == dict2

        if isinstance(dict1, dict) and not isinstance(dict2, dict):
            return False

        if not isinstance(dict1, dict) and isinstance(dict2, dict):
            return False

        # compare if set of keys is the same
        if set(dict1.keys()) != set(dict2.keys()):
            return False

        # compare all values
        for key in dict1.keys():

            # use special comparison for numpy arrays
            if isinstance(dict1[key], np.ndarray):
                if not np.array_equal(dict1[key], dict2[key]):
                    return False
            else:
                if dict1[key] != dict2[key]:
                    return False

        return True


def list_equal(list_a, list_b):
    '''
    Checks if the content of two lists are equal. Can also handle numpy arrays as content.

    :param list_a: List 1.
    :param list_b: List 2.
    :return: True if the content of both lists are equal, otherwise False.
    '''

    if len(list_a) != len(list_b):
        return False

    for idx in range(len(list_a)):

        if type(list_a[idx]) != type(list_b[idx]):
            return False
        if isinstance(list_a[idx], list):
            if not list_equal(list_a[idx], list_b[idx]):
                return False
        elif isinstance(list_a[idx], tuple):
            if not list_equal(list_a[idx], list_b[idx]):
                return False
        elif isinstance(list_a[idx], np.ndarray):
            if not np.array_equal(list_a[idx], list_b[idx], equal_nan=True):
                return False
        elif list_a[idx] != list_b[idx]:
            return False

    return True



def replace_str_from_dict(string, dictionary, pattern_format='{}'):
    '''Replaces string occurances that are given as a dictionary.'''
    out_string = string

    for key_name, new_str in dictionary.items():
        out_string = out_string.replace(pattern_format.format(key_name),
                                        '{}'.format(new_str))

    return out_string



def str_to_slices(slices_str):
    '''
    Creates a slices for lists and numpy arrays from a string.

    >>> out = str_to_slices('[:,-1,0]')
    >>> print(out) # [slice(None), slice(-1), slice(0)]

    :param slice_str: String that describes the slices.
    :return: List of slices.
    '''

    # remove all spaces
    slices_str = slices_str.replace(' ', '')

    if slices_str[0] != '[' or slices_str[-1] != ']':
        raise ValueError('Wrong slice format given. Needs to start witt\'[\' and end with \']\'!')

    # seperate each sub slice
    slice_strings = []
    cur_slice_str = ''
    is_inner_idx_list = False
    for c in slices_str[1:-1]:
        if c == ',' and not is_inner_idx_list:
            slice_strings.append(cur_slice_str)
            cur_slice_str = ''
        elif c == '[':
            is_inner_idx_list = True
            cur_slice_str += c
        elif c == ']':
            is_inner_idx_list = False
            cur_slice_str += c
        else:
            cur_slice_str += c
    slice_strings.append(cur_slice_str)

    slices = []
    for slice_str in slice_strings:

        if slice_str == ':':
            # slice_str: '[:]'
            slices.append(slice(None))
        elif ':' in slice_str:
            # slice_str: '[3:]' or '[3:5]' or '[3:10:2]'
            slice_params = []
            slice_str_params = slice_str.split(':')
            for str_p in slice_str_params:
                if str_p != '':
                    slice_params.append(int(str_p))
                else:
                    slice_params.append(None)

            slices.append(slice(*slice_params))
        else:
            if slice_str[0] == '[' and slice_str[-1] == ']':
                # list with indexes for numpy array indexing, e.g. '[[1,2,4]]'
                idxs = []
                for idx_str in slice_str[1:-1].split(','):
                   if idx_str != '':
                       idxs.append(int(idx_str))
                slices.append(idxs)
            else:
                # slice_str: '[3]'
                slices.append(int(slice_str))

    return slices


def get_dict_variable(base_dict, variable_str):
    '''
    Retrieves items from sub-dictionaries in a dictionary using a single string.

    >>> d = {'sub_dict_1': {'sub_dict_2': {'item_1': 0}}}
    >>> print(get_dict_variable(d, 'sub_dict_1.sub_dict_2.item_1'))

    Allows also to index items in lists.

    >>> d = {'sub_dict_1': {'item_list': ['a', 'b', 'c']}}
    >>> print(get_dict_variable(d, 'sub_dict_1.item_list[0]'))
    >>> print(get_dict_variable(d, 'sub_dict_1.item_list[-1]'))

    :param base_dict: Dictionary with sub-dictionaries.
    :param variable_str: Path to item. Uses '.' to split sub dictionary keys and the item key.
    :return: Item value.
    '''

    # TODO: Feature - allow lists of lists, e.g. 'sub_var.var[:][1]'

    # get the string describing the first sub element in the given variable string
    variable_subelement_strings = variable_str.split('.')
    cur_subelement_str = variable_subelement_strings[0]

    # check if the sub element string contains slices:
    if '[' in cur_subelement_str:
        slice_start = cur_subelement_str.find('[')

        sub_var_name = cur_subelement_str[:slice_start]
        slices = str_to_slices(cur_subelement_str[slice_start:])

        cur_value = base_dict[sub_var_name]

        if isinstance(cur_value, np.ndarray):
            cur_value = cur_value[tuple(slices)]
        else:
            for slice_obj in slices:
                try:
                    cur_value = cur_value[slice_obj]
                except TypeError:
                    raise IndexError()
    else:
        cur_value = base_dict[cur_subelement_str]

    if len(variable_subelement_strings) > 1:
        # not all sub elements processed yet
        cur_value = get_dict_variable(cur_value, '.'.join(variable_subelement_strings[1:]))

    return cur_value



def do_subdict_boolean_filtering(data, filter):
    '''
    Filters a list of dictionaries using conditions based on items in the dictionaries.

    >>> d = [dict(x=1, y=1), dict(x=2, y=3), dict(x=3, y=9))]
    >>> filter1 = do_subdict_boolean_filtering(d, ('x', '==', 1))
    >>> filter2 = do_subdict_boolean_filtering(d, ('x', '==', 'y'))

    :param data: List with dictionaries.
    :param filter: Tuple with filter condition.
    :return: Boolean indices.
    '''

    if isinstance(filter, tuple):

        if len(filter) == 3:

            bool_component_1 = do_subdict_boolean_filtering(data, filter[0])
            bool_component_2 = do_subdict_boolean_filtering(data, filter[2])

            if filter[1] == 'and':
                ret_val = bool_component_1 & bool_component_2
            elif filter[1] == 'or':
                ret_val = bool_component_1 | bool_component_2
            elif filter[1] == '<':
                ret_val = bool_component_1 < bool_component_2
            elif filter[1] == '<=':
                ret_val = bool_component_1 <= bool_component_2
            elif filter[1] == '>':
                ret_val = bool_component_1 > bool_component_2
            elif filter[1] == '>=':
                ret_val = bool_component_1 >= bool_component_2
            elif filter[1] == '==':
                ret_val = bool_component_1 == bool_component_2
            elif filter[1] == '!=':
                ret_val = bool_component_1 != bool_component_2
            elif filter[1] == '+':
                ret_val = bool_component_1 + bool_component_2
            elif filter[1] == '-':
                ret_val = bool_component_1 - bool_component_2
            elif filter[1] == '*':
                ret_val = bool_component_1 * bool_component_2
            elif filter[1] == '/':
                ret_val = bool_component_1 / bool_component_2
            elif filter[1] == '%':
                ret_val = bool_component_1 % bool_component_2
            else:
                raise ValueError('Unknown operator {!r}!'.format(filter[1]))

        elif len(filter) == 2:

            val_component_1 = do_subdict_boolean_filtering(data, filter[1])

            if filter[0] == 'sum':
                ret_val = np.sum(val_component_1)
            elif filter[0] == 'cumsum':
                ret_val = np.cumsum(val_component_1)
            elif filter[0] == 'max':
                ret_val = np.max(val_component_1)
            elif filter[0] == 'min':
                ret_val = np.min(val_component_1)
            else:
                raise ValueError('Unknown operator {!r}!'.format(filter[0]))

        else:
            raise ValueError('Unknown filter command {!r}!'.format(filter))

    else:

        is_var = False
        if isinstance(filter, str):

            # check if string is a variable in the data
            is_var = True
            try:
                # try if the string can be used to find a variable in the data
                # if yes --> the string is a variable
                # if no, these expressions will result in an error and the string is not a variable but some value
                if isinstance(data, list) or isinstance(data, np.ndarray):
                    get_dict_variable(data[0], filter)
                else:
                    # check first item if the data object has a __iter__ method such as the explorationdatahandler
                    for item in data:
                        get_dict_variable(item, filter)
                        break

            except KeyError:
                is_var = False

        if is_var:
            # if the string is a variable then get the data of the variable:
            ret_val = np.zeros(len(data))

            for data_idx, cur_data in enumerate(data):
                ret_val[data_idx] = get_dict_variable(cur_data, filter)
        else:
            ret_val = filter

    return ret_val
