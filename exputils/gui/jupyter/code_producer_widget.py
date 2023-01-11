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

# TODO: when creating a new code cell, also save directly the selection of experiments and repetitions for it

class CodeProducerWidget(ipywidgets.Box):

    @staticmethod
    def default_config():
        dc = eu.AttrDict()

        dc.code_templates = []

        dc.main_box = eu.AttrDict()

        dc.title = 'Code Production'
        dc.accordion = eu.AttrDict(
            selected_index=None,
            layout=eu.AttrDict(width='99%'))
        dc.accordion_box = eu.AttrDict(
            layout=eu.AttrDict(
                width='99%',
                display='flex',
                flex_flow='column',
                align_items='stretch'))
        dc.default_button = eu.AttrDict(
            layout=eu.AttrDict(
                width='95%'))

        return dc

    def __init__(self, code_variables, config=None, **kwargs):
        self.config = eu.combine_dicts(kwargs, config, self.default_config())
        super().__init__(cildren=[], **self.config.main_box)

        self.code_variables = code_variables

        if isinstance(self.config.code_templates, dict): self.config.code_templates = [self.config.code_templates]

        child_widgets = []
        if len(self.config.code_templates) == 1:
            # only create a button
            btn = self._create_button(
                1,
                self.config.code_templates[0],
                default_label=self.config.title)
            child_widgets.append(btn)
        else:

            accordion_child_widgets = []
            for btn_idx, btn_descr in enumerate(self.config.code_templates):
                btn = self._create_button(
                    btn_idx + 1,
                    btn_descr)
                accordion_child_widgets.append(btn)

            accordion_box = ipywidgets.Box(
                children=accordion_child_widgets,
                **self.config.accordion_box)

            accordion = ipywidgets.Accordion(
                children=[accordion_box],
                **self.config.accordion)
            accordion.set_title(0, self.config.title)

            child_widgets.append(accordion)

        eu.gui.jupyter.add_children_to_widget(self, child_widgets)


    def _create_button(self, idx, btn_descr, default_label=None):

        if default_label is None:
            default_label = 'Code {}'.format(idx)

        if isinstance(btn_descr, str):
            # just the template as string
            btn_label = default_label
            btn_tooltip = ''
            btn_code_template = btn_descr
        else:
            # dictionary with description
            btn_label = btn_descr.get('name', default_label)
            btn_tooltip = btn_descr.get('tooltip', '')
            btn_code_template = btn_descr['code_template']

        btn = ipywidgets.Button(
            description=btn_label,
            tooltip=btn_tooltip,
            **self.config.default_button)
        btn.code_template = btn_code_template

        btn.on_click(self.on_click_handler)

        return btn


    def on_click_handler(self, btn):

        code_template = btn.code_template

        if isinstance(self.code_variables, dict):
            code_variables = self.code_variables
        else:
            code_variables = self.code_variables()

        code = eu.misc.replace_str_from_dict(
            code_template,
            code_variables,
            pattern_format='<{}>')

        eu.gui.jupyter.create_new_cell(code)