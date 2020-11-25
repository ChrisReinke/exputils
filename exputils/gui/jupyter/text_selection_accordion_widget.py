# TODO: finish text selction accordion widget

# # default_config = eu.AttrDict(
# #     datasource_label='<datasource>',
# #     # either string with template for all data sources or a list with a string for each label
# #     experiment_label='<name>',
# #     repetition_label='<id>',
#
# import ipywidgets
# import exputils as eu
#
# class TextSelectionAccordionWidget(ipywidgets.Accordion):
#
#     @staticmethod
#     def default_config():
#         dc = eu.AttrDict()
#
#
#         dc.default_selection_element_hbox = eu.AttrDict(
#             layout=eu.AttrDict(width='100%')
#         )
#
#         dc.default_selection_element_label = eu.AttrDict(
#             layout=eu.AttrDict(width='25%')
#         )
#
#         dc.default_selection_element_text = eu.AttrDict(
#             layout=eu.AttrDict(width='75%')
#         )
#
#
#
#         dc.selection_elements = []
#         #   eu.AttrDict(
#         #
#         #       )
#
#         dc.main_accordion = eu.AttrDict()
#
#     def __init__(self, config=None, **kwargs):
#         self.config = self.default_config(kwargs, config, self.default_config())
#
#         super().__init__(children=[], **self.config.main_accordion)
#
#         # create the selection elements
#
#         self.selection_text_widgets = eu.AttrDict()
#
#
#         for elem_descr in self.config.selection_elements:
#
#             label = ipywidgets.Label(
#                 value=elem_descr.label
#             )
#
#             hbox = ipywidgets.HBox(
#
#             )
#
#
#     @property
#     def selection(self):
#         selection = eu.AttrDict()
#         for elem_descr in self.config.selection_elements:
#             selection[elem_descr['name']] = self.selection_text_widgets[elem_descr['name']].value
#         return selection
#
#
#     @selection.setter
#     def selection(self, selection):
#         for elem_name, elem_value in selection.items():
#             self.selection_text_widgets[elem_name].value = elem_value
#
#
#
