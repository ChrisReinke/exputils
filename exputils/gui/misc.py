##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
def transform_color_str_to_tuple(colors):
    is_input_list = isinstance(colors, list)

    if not is_input_list:
        colors = [colors]

    out_color = []
    for color in colors:
        col_elements = color.replace('(', ',').replace(')', ',').split(',')
        out_color.append((col_elements[0], int(col_elements[1]), int(col_elements[2]), int(col_elements[3])))

    if is_input_list:
        return out_color
    else:
        return out_color[0]


def transform_color_tuple_to_str(colors):
    is_input_list = isinstance(colors, list)

    if not is_input_list:
        colors = [colors]

    out_color = ['{}({}, {}, {})'.format(color[0], color[1], color[2], color[3]) for color in colors]

    if is_input_list:
        return out_color
    else:
        return out_color[0]
