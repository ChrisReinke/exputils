#TODO: Feature - finish text selction accordion widget
#TODO: title updated by content of the variables
#TODO: events for change of values

# default_config = eu.AttrDict(
#     datasource_label='<datasource>',
#     # either string with template for all data sources or a list with a string for each label
#     experiment_label='<name>',
#     repetition_label='<id>',

import ipywidgets
import exputils as eu

class TextSelectionAccordionWidget(ipywidgets.Accordion):

    @staticmethod
    def default_config():
        dc = eu.AttrDict()

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
        #   eu.AttrDict(
        #
        #       )

        return dc

    def __init__(self, config=None, **kwargs):
        self.config = eu.combine_dicts(kwargs, config, self.default_config())

        super().__init__( **self.config.main_accordion)

        # create the selection elements

        self.selection_text_widgets = dict()

        selection_hbox_widgets = []

        for elem_descr in self.config.selection_elements:

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

        main_vbox = ipywidgets.VBox(
            children=selection_hbox_widgets,
            **self.config.main_vbox
        )

        eu.gui.jupyter.add_children_to_widget(self, main_vbox)


    @property
    def selection(self):
        selection = eu.AttrDict()
        for elem_descr in self.config.selection_elements:
            selection[elem_descr['name']] = self.selection_text_widgets[elem_descr['name']].value
        return selection


    @selection.setter
    def selection(self, selection):
        for elem_name, elem_value in selection.items():
            self.selection_text_widgets[elem_name].value = elem_value



