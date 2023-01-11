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
import os
import IPython
from datetime import datetime
import ipywidgets
import base64
from IPython.display import Javascript, display

def create_new_cell(code='', where='below'):
    """Create a code cell in the IPython Notebook.

    Parameters
    code: unicode
        Code to fill the new code cell with.
    where: unicode
        Where to add the new code cell.
        Possible values include:
            at_bottom
            above
            below"""
    encoded_code = (base64.b64encode(str.encode(code))).decode()

    out = ipywidgets.Output()
    with out:
        IPython.display.display_javascript("""
                var code = IPython.notebook.insert_cell_{0}('code');
                code.set_text(atob("{1}"));
            """.format(where, encoded_code), raw=True)
    out.clear_output()


def save_config(config, name, directory=None, profile=None):
    '''
    Saves a given config object as a JSON. The config is usually a dictionary.

    :param name: Name of the configuration.
    :param config: Dictionary with the configuration.
    :param directory:  Optional directory where config is stored. (Default: './.ipython_config/').
    :param profile: Optional profile under which configuration is stored. (Default: name of the current notebook file).
    :return:
    '''

    if directory is None: directory = eu.gui.jupyter.DEFAULT_CONFIG_DIRECTORY
    if profile is None: profile = eu.gui.jupyter.get_notebook_name()

    filepath = os.path.join(directory, profile, name + '.json')

    eu.io.save_dict_as_json_file(config, filepath)


def load_config(name, directory=None, profile=None):
    '''
    Loads a configuration that is stored as JSON file as a AttrDict (dictionary).
    Return an empty AttrDict (dictionary) if the configuration does not exists.

    :param name: Name of the configuration.
    :param directory:  Optional directory where config is stored. (Default: './.ipython_config/').
    :param profile: Optional profile under which configuration is stored. (Default: name of the current notebook file).
    :return: AttrDict (dictionary) with config.
    '''

    if directory is None: directory = eu.gui.jupyter.DEFAULT_CONFIG_DIRECTORY
    if profile is None: profile = eu.gui.jupyter.get_notebook_name()

    filepath = os.path.join(directory, profile, name + '.json')

    try:
        loaded_dict = eu.io.load_dict_from_json_file(filepath)
    except FileNotFoundError:
        loaded_dict = {}

    return eu.AttrDict(loaded_dict)


def remove_children_from_widget(widget, idxs):
    '''
    Removes children widgets from a given widget according to their index.

    :param widget: Widget from whcih the children should be removed.
    :param idxs: Indexes (or single index) of child widgets that should be removed.
    '''

    if not isinstance(idxs, list):
        idxs = [idxs]

    children = list(widget.children)

    idxs = idxs.copy()
    idxs.sort(reverse=True)
    for idx in idxs:
        del children[idx]

    widget.children = tuple(children)


def add_children_to_widget(widget, children, idx=None):
    '''
    Adds children widgets to the given widget.

    :param widget: ipywidget to whoms children attribute the given children should be added.
    :param children: Child widgets or list of child widgets that should be added to the given widget.
    :param idx: Position at which the given children should be added. If None is given then at the end. (default = None)
    '''

    if not isinstance(children, list):
        children = [children]

    existing_children_list = list(widget.children)

    if idx is None:
        new_children_list = existing_children_list + children
    else:
        new_children_list = existing_children_list
        new_children_list[idx:idx] = children

    widget.children = tuple(new_children_list)


def set_children_of_widget(widget, idxs, children):
    children_widgets =  list(widget.children)
    children_widgets[idxs] = children
    widget.children = tuple(children_widgets)


def generate_random_state_backup_name():
    time_in_sec = int(datetime.now().timestamp() - datetime(2020, 1, 1).timestamp())
    return 'state_backup_{}'.format(time_in_sec)

