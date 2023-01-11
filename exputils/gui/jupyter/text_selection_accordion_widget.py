##
## This file is part of the exputils package.
##
## Copyright: INRIA
## Year: 2022, 2023
## Contact: chris.reinke@inria.fr
##
## exputils is provided under GPL-3.0-or-later
##
import ipywidgets
import exputils as eu

#TODO: Feature - events for change of values

class TextSelectionAccordionWidget(ipywidgets.Accordion):

    @staticmethod
    def default_config():
        dc = eu.AttrDict()

        dc.title = '<selection>'

        dc.main_accordion = eu.AttrDict(
            #layout=eu.AttrDict(width='100%')
        )

        dc.main_vbox = eu.AttrDict(
            layout=eu.AttrDict(width='100%')
        )

        dc.default_selection_element_hbox = eu.AttrDict(
            layout=eu.AttrDict(width='100%')
        )

        dc.default_selection_element_label = eu.AttrDict(
            layout=eu.AttrDict(width='25%')
        )

        dc.default_selection_element_text = eu.AttrDict(
            layout=eu.AttrDict(width='75%')
        )

        dc.selection_elements = []

        return dc

    def __init__(self, config=None, **kwargs):
        self.config = eu.combine_dicts(kwargs, config, self.default_config())

        super().__init__( **self.config.main_accordion)

        # create the selection elements

        self.selection_text_widgets = dict()

        selection_hbox_widgets = []

        # create selection_elements as list of AttrDicts to have a consitent datatype
        self.selection_elements = []
        for elem_descr in self.config.selection_elements:

            if isinstance(elem_descr, str):
                elem_name = elem_descr
                elem_label = elem_descr
                elem_title_label = elem_descr
            else:
                elem_name = elem_descr['name']
                elem_label = elem_descr.get('label', elem_name)
                elem_title_label = elem_descr.get('title_label', elem_label)

            self.selection_elements.append(eu.AttrDict(
                name=elem_name,
                label = elem_label,
                title_label = elem_title_label))

        # create the gui elements
        for elem_descr in self.selection_elements:

            label = ipywidgets.Label(
                value=elem_descr.label,
                **self.config.default_selection_element_label
            )

            text_widget = ipywidgets.Text(
                value='',
                **self.config.default_selection_element_text
            )

            hbox = ipywidgets.HBox(
                children=[label, text_widget],
                **self.config.default_selection_element_hbox
            )

            selection_hbox_widgets.append(hbox)
            self.selection_text_widgets[elem_descr.name] = text_widget

            text_widget.observe(
                self._on_text_value_changed,
                names='value')

        main_vbox = ipywidgets.VBox(
            children=selection_hbox_widgets,
            **self.config.main_vbox
        )

        eu.gui.jupyter.add_children_to_widget(self, main_vbox)


    @property
    def selection(self):
        selection = eu.AttrDict()
        for elem_descr in self.selection_elements:
            selection[elem_descr.name] = self.selection_text_widgets[elem_descr.name].value
        return selection


    @selection.setter
    def selection(self, selection):
        for elem_name, elem_value in selection.items():
            self.selection_text_widgets[elem_name].value = elem_value


    def _on_text_value_changed(self, event_descr):
        self._update_title()


    def _update_title(self):

        if self.config.title is None:
            title_str = ''
        else:
            title_str = self.config.title

            # create selection title
            if '<selection>' in title_str:

                selection_str_elements = []
                for elem_descr in self.selection_elements:

                    if elem_descr.title_label.endswith(':'):
                        delimiter = ''
                    else:
                        delimiter = ':'

                    selection_str_elements.append('{}{} {}'.format(
                        elem_descr.title_label,
                        delimiter,
                        self.selection_text_widgets[elem_descr.name].value))

                title_str = title_str.replace(
                    '<selection>',
                    ', '.join(selection_str_elements))

        self.set_title(0, title_str)