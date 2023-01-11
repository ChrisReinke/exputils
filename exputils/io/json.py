##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import exputils as eu
import numpy as np
import base64
import cloudpickle
try:
    import json
except ImportError:
    import simplejson as json


class ExputilsJSONEncoder(json.JSONEncoder):
    """
    Encodes objects into json strings. Allows to encode numpy arrays and functions.
    The exputils_json_object_hook() function can be used to load the dumped objects.
    Usage:
    >>> dumped = json.dumps(object, cls=ExputilsJSONEncoder)
    >>> loaded = json.loads(dumped, object_hook=exputils_json_object_hook)
    """

    def default(self, obj):
        """
        if input object is a ndarray it will be converted into a dict holding dtype, shape and the data base64 encoded
        """
        if isinstance(obj, np.ndarray):
            data_b64 = base64.b64encode(np.ascontiguousarray(obj).data)
            return dict(__ndarray__=data_b64.decode('ascii'),
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError

        if isinstance(obj, np.int64):
            return int(obj)

        if isinstance(obj, np.float64):
            return float(obj)

        if callable(obj):
            b = cloudpickle.dumps(obj)
            s = base64.b64encode(b).decode()
            return dict(__cloudpickle__=s)

        return super().default(obj)


def exputils_json_object_hook(dct):
    """
    Decodes json data. Allows to decode numpy arrays and functions.

    Usage:
    >>> dumped = json.dumps(object, cls=ExputilsJSONEncoder)
    >>> loaded = json.loads(dumped, object_hook=exputils_json_object_hook)
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])

    if isinstance(dct, dict) and '__cloudpickle__' in dct:
        b = base64.b64decode(dct['__cloudpickle__'])
        expr = cloudpickle.loads(b)
        return expr

    return dct


def save_dict_as_json_file(dict, filepath, **kwargs):
    """ Saves a dict to a JSON file. Accepts the same keyword options as `json.dumps()`."""

    # allow saving of numpy arrays in JSON file
    if 'cls' not in kwargs:
        kwargs['cls'] = eu.io.json.ExputilsJSONEncoder

    json_content = json.dumps(dict, **kwargs)

    eu.io.makedirs_for_file(filepath)

    f = open(filepath, "w")
    f.write(json_content)
    f.close()


def load_dict_from_json_file(filepath, is_transform_ints=False, **kwargs):
    """
    Loads a dictionary from a JSON file.

    :param filepath: Path to the file.
    :param is_transform_ints: JSON does not allow to store integers a dictionary keus.
                              If this option is set to True any keys in the JSON are tried to conver to integers if possible.
    :param kwargs: Optional arguments that are passed to the json.loads function.
    :return: Loaded dictionary.
    """

    if 'cls' not in kwargs:
        kwargs['object_hook'] = eu.io.json.exputils_json_object_hook

    # Open the file in read mode
    file_object = open(filepath, 'r')
    json_content = file_object.read()
    file_object.close()

    loaded_dict = json.loads(json_content, **kwargs)

    # chenge possible int keys to ints as json changes ints to strings
    if is_transform_ints:
        loaded_dict = convert_json_dict_keys_to_ints(loaded_dict)

    return loaded_dict


def convert_json_dict_keys_to_ints(json_data):
    '''
    JSON does not allow ints as keys for dictionaries. This method transforms all keys in the given json data to ints if such a conversion is possible.

    :param json_data:
    :return:
    '''

    correctedDict = {}

    for key, value in json_data.items():
        if isinstance(value, list):
            value = [convert_json_dict_keys_to_ints(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, dict):
            value = convert_json_dict_keys_to_ints(value)
        try:
            key = int(key)
        except Exception as ex:
            pass
        correctedDict[key] = value

    return correctedDict

