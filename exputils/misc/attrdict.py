##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##

# This code was adapted from https://github.com/Infinidat/munch
#
# Copyright (c) 2010 David Schoonover
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import exputils
import yaml
from collections import defaultdict
from collections.abc import Mapping
from six import iteritems, iterkeys  # pylint: disable=unused-import
from copy import deepcopy
try:
    import json
except ImportError:
    import simplejson as json

class AttrDict(dict):
    """ A dictionary that provides attribute-style access.
        >>> b = AttrDict()
        >>> b.hello = 'world'
        >>> b.hello
        'world'
        >>> b['hello'] += "!"
        >>> b.hello
        'world!'
        >>> b.foo = AttrDict(lol=True)
        >>> b.foo.lol
        True
        >>> b.foo is b['foo']
        True
        A AttrDict is a subclass of dict; it supports all the methods a dict does...
        >>> sorted(b.keys())
        ['foo', 'hello']
        Including update()...
        >>> b.update({ 'ponies': 'are pretty!' }, hello=42)
        >>> print (repr(b))
        AttrDict({'ponies': 'are pretty!', 'foo': Munch({'lol': True}), 'hello': 42})
        As well as iteration...
        >>> sorted([ (k,b[k]) for k in b ])
        [('foo', AttrDict({'lol': True})), ('hello', 42), ('ponies', 'are pretty!')]
        And "splats".
        >>> "The {knights} who say {ni}!".format(**AttrDict(knights='lolcats', ni='can haz'))
        'The lolcats who say can haz!'
        See unmunchify/AttrDict.toDict, munchify/AttrDict.fromDict for notes about conversion.
    """

    # only called if k not found in normal places
    def __getattr__(self, k):
        """ Gets key if it exists, otherwise throws AttributeError.
            nb. __getattr__ is only called if key is not found in normal places.
            >>> b = AttrDict(bar='baz', lol={})
            >>> b.foo
            Traceback (most recent call last):
                ...
            AttributeError: foo
            >>> b.bar
            'baz'
            >>> getattr(b, 'bar')
            'baz'
            >>> b['bar']
            'baz'
            >>> b.lol is b['lol']
            True
            >>> b.lol is getattr(b, 'lol')
            True
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)


    def __setattr__(self, k, v):
        """ Sets attribute k if it exists, otherwise sets key k. A KeyError
            raised by set-item (only likely if you subclass Munch) will
            propagate as an AttributeError instead.
            >>> b = AttrDict(foo='bar', this_is='useful when subclassing')
            >>> hasattr(b.values, '__call__')
            True
            >>> b.values = 'uh oh'
            >>> b.values
            'uh oh'
            >>> b['values']
            Traceback (most recent call last):
                ...
            KeyError: 'values'
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)


    def __delattr__(self, k):
        """ Deletes attribute k if it exists, otherwise deletes key k. A KeyError
            raised by deleting the key--such as when the key is missing--will
            propagate as an AttributeError instead.
            >>> b = AttrDict(lol=42)
            >>> del b.lol
            >>> b.lol
            Traceback (most recent call last):
                ...
            AttributeError: lol
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)


    def toDict(self):
        """ Recursively converts a munch back into a dictionary.
            >>> b = AttrDict(foo=AttrDict(lol=True), hello=42, ponies='are pretty!')
            >>> sorted(b.toDict().items())
            [('foo', {'lol': True}), ('hello', 42), ('ponies', 'are pretty!')]
            See unmunchify for more info.
        """
        return attrdict_to_dict(self)


    @property
    def __dict__(self):
        return self.toDict()


    def __repr__(self):
        """ Invertible* string-form of a Munch.
            >>> b = AttrDict(foo=AttrDict(lol=True), hello=42, ponies='are pretty!')
            >>> print (repr(b))
            Munch({'ponies': 'are pretty!', 'foo': Munch({'lol': True}), 'hello': 42})
            >>> eval(repr(b))
            Munch({'ponies': 'are pretty!', 'foo': Munch({'lol': True}), 'hello': 42})
            >>> with_spaces = AttrDict({1: 2, 'a b': 9, 'c': AttrDict({'simple': 5})})
            >>> print (repr(with_spaces))
            Munch({'a b': 9, 1: 2, 'c': Munch({'simple': 5})})
            >>> eval(repr(with_spaces))
            Munch({'a b': 9, 1: 2, 'c': Munch({'simple': 5})})
            (*) Invertible so long as collection contents are each repr-invertible.
        """
        return '{0}({1})'.format(self.__class__.__name__, dict.__repr__(self))


    def __dir__(self):
        return list(iterkeys(self))


    def __getstate__(self):
        """ Implement a serializable interface used for pickling.
        See https://docs.python.org/3.6/library/pickle.html.
        """
        return {k: v for k, v in self.items()}


    def __setstate__(self, state):
        """ Implement a serializable interface used for pickling.
        See https://docs.python.org/3.6/library/pickle.html.
        """
        self.clear()
        self.update(state)


    __members__ = __dir__  # for python2.x compatibility


    def __eq__(self, other):
        '''Is the dict equal to another dict. Allows to compare numpy arrays.'''
        return exputils.misc.dict_equal(self, other)


    @classmethod
    def from_dict(cls, d):
        """ Recursively transforms a dictionary into a AttrDict via copy.
            >>> b = AttrDict.from_dict({'urmom': {'sez': {'what': 'what'}}})
            >>> b.urmom.sez.what
            'what'
            See dict_to_attrdict for more info.
        """
        return dict_to_attrdict(d, cls)


    def copy(self):
        return type(self).from_dict(self)


    def to_json(self, **options):
        """ Serializes this AttrDict to JSON. Accepts the same keyword options as `json.dumps()`.
            >>> b = AttrDict(foo=AttrDict(lol=True), hello=42, ponies='are pretty!')
            >>> json.dumps(b) == b.to_json()
            True

            Allows to dump numpy arrays into JSON.
        """

        # allow to dump numpy into json
        if 'cls' not in options:
            options['cls'] = exputils.io.json.ExputilsJSONEncoder

        return json.dumps(self, **options)


    @classmethod
    def from_json(cls, json_data, is_transform_ints=True, **options):
        """ Loads an AttrDict from JSON. Accepts the same keyword options as `json.loads()`."""

        # allow to load numpy from json
        if 'cls' not in options:
            options['object_hook'] = exputils.io.json.exputils_json_object_hook

        loaded_json = json.loads(json_data, **options)

        # chenge possible int keys to ints as json changes ints to strings
        if is_transform_ints:
            loaded_json = exputils.io.convert_json_dict_keys_to_ints(loaded_json)

        return dict_to_attrdict(loaded_json, cls)


    def to_json_file(self, filepath, **options):
        exputils.io.save_dict_as_json_file(self, filepath, **options)


    @classmethod
    def from_json_file(cls, filepath, **options):
        loaded_dict = exputils.io.load_dict_from_json_file(filepath, **options)
        return dict_to_attrdict(loaded_dict, cls)


    def to_yaml(self, path) -> None:

        with open(path, 'w') as output_file:
            yaml.dump(self.toDict(), output_file)

    @classmethod
    def from_yaml(cls, filepath, **options):
        with open(filepath, 'r') as config_file:
            loaded_dict = yaml.load(config_file.read(),
                                    yaml.FullLoader)
        return dict_to_attrdict(loaded_dict, cls)


class AutoAttrDict(AttrDict):
    def __setattr__(self, k, v):
        """ Works the same as AttrDict.__setattr__ but if you supply
            a dictionary as value it will convert it to another AttrDict.
        """
        if isinstance(v, dict) and not isinstance(v, (AutoAttrDict, AttrDict)):
            v = dict_to_attrdict(v, AutoAttrDict)
        super(AutoAttrDict, self).__setattr__(k, v)


class DefaultAttrDict(AttrDict):
    """
    A AttrDict that returns a user-specified value for missing keys.
    """


    def __init__(self, *args, **kwargs):
        """ Construct a new DefaultAttrDict. Like collections.defaultdict, the
            first argument is the default value; subsequent arguments are the
            same as those for dict.
        """
        # Mimic collections.defaultdict constructor
        if args:
            default = args[0]
            args = args[1:]
        else:
            default = None
        super(DefaultAttrDict, self).__init__(*args, **kwargs)
        self.__default__ = default


    def __getattr__(self, k):
        """ Gets key if it exists, otherwise returns the default value."""
        try:
            return super(DefaultAttrDict, self).__getattr__(k)
        except AttributeError:
            return self.__default__


    def __setattr__(self, k, v):
        if k == '__default__':
            object.__setattr__(self, k, v)
        else:
            return super(DefaultAttrDict, self).__setattr__(k, v)


    def __getitem__(self, k):
        """ Gets key if it exists, otherwise returns the default value."""
        try:
            return super(DefaultAttrDict, self).__getitem__(k)
        except KeyError:
            return self.__default__


    def __getstate__(self):
        """ Implement a serializable interface used for pickling.
        See https://docs.python.org/3.6/library/pickle.html.
        """
        return (self.__default__, {k: v for k, v in self.items()})


    def __setstate__(self, state):
        """ Implement a serializable interface used for pickling.
        See https://docs.python.org/3.6/library/pickle.html.
        """
        self.clear()
        default, state_dict = state
        self.update(state_dict)
        self.__default__ = default


    @classmethod
    def from_dict(cls, d, default=None):
        # pylint: disable=arguments-differ
        return dict_to_attrdict(d, factory=lambda d_: cls(default, d_))


    def copy(self):
        return type(self).from_dict(self, default=self.__default__)


    def __repr__(self):
        return '{0}({1!r}, {2})'.format(
            type(self).__name__, self.__undefined__, dict.__repr__(self))


class DefaultFactoryAttrDict(defaultdict, AttrDict):
    """ A AttrDict that calls a user-specified function to generate values for
        missing keys like collections.defaultdict.
        >>> b = DefaultFactoryAttrDict(list, {'hello': 'world!'})
        >>> b.hello
        'world!'
        >>> b.foo
        []
        >>> b.bar.append('hello')
        >>> b.bar
        ['hello']
    """


    def __init__(self, default_factory, *args, **kwargs):
        # pylint: disable=useless-super-delegation
        super(DefaultFactoryAttrDict, self).__init__(default_factory, *args, **kwargs)


    @classmethod
    def from_dict(cls, d, default_factory):
        # pylint: disable=arguments-differ
        return dict_to_attrdict(d, factory=lambda d_: cls(default_factory, d_))


    def copy(self):
        return type(self).from_dict(self, default_factory=self.default_factory)


    def __repr__(self):
        factory = self.default_factory.__name__
        return '{0}({1}, {2})'.format(
            type(self).__name__, factory, dict.__repr__(self))


# While we could convert abstract types like Mapping or Iterable, I think
# munchify is more likely to "do what you mean" if it is conservative about
# casting (ex: isinstance(str,Iterable) == True ).
#
# Should you disagree, it is not difficult to duplicate this function with
# more aggressive coercion to suit your own purposes.

def dict_to_attrdict(x, factory=AttrDict):
    """ Recursively transforms a dictionary into a AttrDict via copy.
        >>> b = dict_to_attrdict({'urmom': {'sez': {'what': 'what'}}})
        >>> b.urmom.sez.what
        'what'
        munchify can handle intermediary dicts, lists and tuples (as well as
        their subclasses), but ymmv on custom datatypes.
        >>> b = dict_to_attrdict({ 'lol': ('cats', {'hah':'i win again'}),
        ...         'hello': [{'french':'salut', 'german':'hallo'}] })
        >>> b.hello[0].french
        'salut'
        >>> b.lol[1].hah
        'i win again'
        nb. As dicts are not hashable, they cannot be nested in sets/frozensets.
    """
    if isinstance(x, dict):
        return factory((k, dict_to_attrdict(v, factory)) for k, v in iteritems(x))
    elif isinstance(x, (list, tuple)):
        return type(x)(dict_to_attrdict(v, factory) for v in x)
    else:
        return x


def attrdict_to_dict(x):
    """ Recursively converts a AttrDict into a dictionary.
        >>> b = AttrDict(foo=AttrDict(lol=True), hello=42, ponies='are pretty!')
        >>> sorted(attrdict_to_dict(b).items())
        [('foo', {'lol': True}), ('hello', 42), ('ponies', 'are pretty!')]
        unmunchify will handle intermediary dicts, lists and tuples (as well as
        their subclasses), but ymmv on custom datatypes.
        >>> b = AttrDict(foo=['bar', AttrDict(lol=True)], hello=42,
        ...         ponies=('are pretty!', AttrDict(lies='are trouble!')))
        >>> sorted(attrdict_to_dict(b).items()) #doctest: +NORMALIZE_WHITESPACE
        [('foo', ['bar', {'lol': True}]), ('hello', 42), ('ponies', ('are pretty!', {'lies': 'are trouble!'}))]
        nb. As dicts are not hashable, they cannot be nested in sets/frozensets.
    """
    if isinstance(x, dict):
        return dict((k, attrdict_to_dict(v)) for k, v in iteritems(x))
    elif isinstance(x, (list, tuple)):
        return type(x)(attrdict_to_dict(v) for v in x)
    else:
        return x


# Serialization

# try:
#     # Attempt to register ourself with PyYAML as a representer
#     import yaml
#     from yaml.representer import Representer, SafeRepresenter
#
#
#     def from_yaml(loader, node):
#         """ PyYAML support for Munches using the tag `!munch` and `!munch.Munch`.
#             >>> import yaml
#             >>> yaml.load('''
#             ... Flow style: !munch.Munch { Clark: Evans, Brian: Ingerson, Oren: Ben-Kiki }
#             ... Block style: !munch
#             ...   Clark : Evans
#             ...   Brian : Ingerson
#             ...   Oren  : Ben-Kiki
#             ... ''') #doctest: +NORMALIZE_WHITESPACE
#             {'Flow style': Munch(Brian='Ingerson', Clark='Evans', Oren='Ben-Kiki'),
#              'Block style': Munch(Brian='Ingerson', Clark='Evans', Oren='Ben-Kiki')}
#             This module registers itself automatically to cover both Munch and any
#             subclasses. Should you want to customize the representation of a subclass,
#             simply register it with PyYAML yourself.
#         """
#         data = Munch()
#         yield data
#         value = loader.construct_mapping(node)
#         data.update(value)
#
#
#     def to_yaml_safe(dumper, data):
#         """ Converts Munch to a normal mapping node, making it appear as a
#             dict in the YAML output.
#             >>> b = Munch(foo=['bar', Munch(lol=True)], hello=42)
#             >>> import yaml
#             >>> yaml.safe_dump(b, default_flow_style=True)
#             '{foo: [bar, {lol: true}], hello: 42}\\n'
#         """
#         return dumper.represent_dict(data)
#
#
#     def to_yaml(dumper, data):
#         """ Converts Munch to a representation node.
#             >>> b = Munch(foo=['bar', Munch(lol=True)], hello=42)
#             >>> import yaml
#             >>> yaml.dump(b, default_flow_style=True)
#             '!munch.Munch {foo: [bar, !munch.Munch {lol: true}], hello: 42}\\n'
#         """
#         return dumper.represent_mapping(u('!munch.Munch'), data)
#
#
#     yaml.add_constructor(u('!munch'), from_yaml)
#     yaml.add_constructor(u('!munch.Munch'), from_yaml)
#
#     SafeRepresenter.add_representer(Munch, to_yaml_safe)
#     SafeRepresenter.add_multi_representer(Munch, to_yaml_safe)
#
#     Representer.add_representer(Munch, to_yaml)
#     Representer.add_multi_representer(Munch, to_yaml)
#
#
#     # Instance methods for YAML conversion
#     def toYAML(self, **options):
#         """ Serializes this Munch to YAML, using `yaml.safe_dump()` if
#             no `Dumper` is provided. See the PyYAML documentation for more info.
#             >>> b = Munch(foo=['bar', Munch(lol=True)], hello=42)
#             >>> import yaml
#             >>> yaml.safe_dump(b, default_flow_style=True)
#             '{foo: [bar, {lol: true}], hello: 42}\\n'
#             >>> b.toYAML(default_flow_style=True)
#             '{foo: [bar, {lol: true}], hello: 42}\\n'
#             >>> yaml.dump(b, default_flow_style=True)
#             '!munch.Munch {foo: [bar, !munch.Munch {lol: true}], hello: 42}\\n'
#             >>> b.toYAML(Dumper=yaml.Dumper, default_flow_style=True)
#             '!munch.Munch {foo: [bar, !munch.Munch {lol: true}], hello: 42}\\n'
#         """
#         opts = dict(indent=4, default_flow_style=False)
#         opts.update(options)
#         if 'Dumper' not in opts:
#             return yaml.safe_dump(self, **opts)
#         else:
#             return yaml.dump(self, **opts)
#
#
#     def fromYAML(*args, **kwargs):
#         return munchify(yaml.load(*args, **kwargs))
#
#
#     Munch.toYAML = toYAML
#     Munch.fromYAML = staticmethod(fromYAML)
#
# except ImportError:
#     pass


def combine_dicts(*args, is_recursive=True, copy_mode='deepcopy'):
    '''
    Combines several AttrDicts recursively.
    Kepps the values of the

    :param args:
    :param is_recursive: Should
    :param copy_mode: Defines how the dictionaries should be copied ('deepcopy', 'copy', 'none').
    :return: Combined AttrDict.
    '''

    args = list(args)

    # convert arguments to AttrDicts if they are not
    for idx in range(len(args)):
        if args[idx] is None:
            args[idx] = AttrDict()
        elif not isinstance(args[idx], AttrDict):
            args[idx] = AttrDict.from_dict(args[idx])

    # copy the dictionaries according to copy mode
    dicts = []
    for dict in args:
        if copy_mode.lower() == 'deepcopy':
            dicts.append(deepcopy(dict))
        elif copy_mode.lower() == 'copy':
            dicts.append(dict.copy())
        elif copy_mode is None or copy_mode.lower() == 'none':
            dicts.append(dict)
        else:
            raise ValueError('Unknown copy mode {!r}!'.format(copy_mode))

    # combine the dicts going from last to first
    for dict_idx in range(len(args)-1, 0, -1):

        for def_key, def_item in dicts[dict_idx].items():

            if not def_key in dicts[dict_idx-1]:
                # add default item if not found target
                dicts[dict_idx - 1][def_key] = def_item
            elif (is_recursive
                  and isinstance(def_item, Mapping)
                  and isinstance(dicts[dict_idx - 1][def_key], Mapping)):
                # If the value is a dictionary in the default and the target, then also set default
                # values for it.
                dicts[dict_idx - 1][def_key] = combine_dicts(dicts[dict_idx - 1][def_key],
                                                             def_item,
                                                             is_recursive=is_recursive,
                                                             copy_mode=copy_mode)

    return dicts[0]
