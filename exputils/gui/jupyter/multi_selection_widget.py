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
import ipywidgets


class MultiSelectionWidget(ipywidgets.VBox):

    @staticmethod
    def default_config():
        dc = eu.AttrDict()

        dc.title = 'SELECTED_CHOICES'  # SELECTED_CHOICES, TITLE_LABELS

        # labels for each possible choice that are then shown in the title if the 'TITLE_LABELS'
        # option is used for the title - configuration
        dc.title_labels = []

        dc.is_select_all_choice = True
        dc.all_selected_title_label = 'all'

        # defines if an extra choice called none is given
        dc.is_select_none_choice = False

        dc.none_selected_title_label = 'none'

        dc.main_vbox = eu.AttrDict()

        dc.checkboxes = eu.AttrDict()

        dc.accordion = eu.AttrDict()

        dc.multi_checkbox_vbox = eu.AttrDict(layout=eu.AttrDict(overflow='scroll'))

        return dc

    def __init__(self, choices=None, config=None, **kwargs):
        self.config = eu.combine_dicts(kwargs, config, self.default_config())

        if choices is None: choices = []

        self.choices = choices

        self._on_selection_changed_event_handlers = []

        # define if the events for checkboxes are active
        self._is_on_select_all_checkbox_changed_active = True
        self._is_on_select_none_checkbox_changed_active = True
        self._is_on_checkbox_changed_active = True

        self._is_selection_changed_event_active = True

        # create checkboxes
        self.choice_checkboxes = []
        for choice_idx, choice in enumerate(self.choices):
            # is_on = not self.config.is_select_all_choice

            chkbox = ipywidgets.Checkbox(
                description=str(choice),
                value=True,
                **self.config.checkboxes)

            chkbox.observe(self._on_checkbox_changed)

            self.choice_checkboxes.append(chkbox)


        checkboxes_list = self.choice_checkboxes

        if self.config.is_select_all_choice:
            self.select_all_checkbox = ipywidgets.Checkbox(
                description='all',
                value=True,
                **self.config.checkboxes)
            self.select_all_checkbox.observe(self._on_select_all_checkbox_changed)
            checkboxes_list = [self.select_all_checkbox] + checkboxes_list

        if self.config.is_select_none_choice:
            self.select_none_checkbox = ipywidgets.Checkbox(
                description='none',
                value=False,
                **self.config.checkboxes)
            self.select_none_checkbox.observe(self._on_select_none_checkbox_changed)
            checkboxes_list = [self.select_none_checkbox] + checkboxes_list

        self.multi_checkbox_vbox_widget = ipywidgets.VBox(
            children=checkboxes_list,
            **self.config.multi_checkbox_vbox)

        self.accordion_widget = ipywidgets.Accordion(
            children=[self.multi_checkbox_vbox_widget],
            selected_index=None,
            **self.config.accordion)
        self.accordion_widget.set_title(0, self.config.title)

        self._update_titel()

        super().__init__(children=[self.accordion_widget], **self.config.main_vbox)


    @property
    def is_all_selected(self):
        return len(self.selected_choices) == len(self.choices)


    @property
    def selected_choices(self):
        choices = []
        for chkbox_idx, chkbox in enumerate(self.choice_checkboxes):
            if chkbox.value:
                choices.append(self.choices[chkbox_idx])
        return choices


    @selected_choices.setter
    def selected_choices(self, selected_choices):

        old_is_selection_changed_event_active = self._is_selection_changed_event_active
        self._is_selection_changed_event_active = False

        if selected_choices == 'all':
            for chkbox in self.choice_checkboxes:
                chkbox.value = True
        elif selected_choices == 'none':
            for chkbox in self.choice_checkboxes:
                chkbox.value = False
        else:
            for choice_idx, choice in enumerate(self.choices):
                if choice in selected_choices:
                    self.choice_checkboxes[choice_idx].value = True
                else:
                    self.choice_checkboxes[choice_idx].value = False

        self._is_selection_changed_event_active = old_is_selection_changed_event_active
        self._call_selection_changed_event()


    @property
    def selected_choices_idxs(self):
        idxs = []
        for chkbox_idx, chkbox in enumerate(self.choice_checkboxes):
            if chkbox.value:
                idxs.append(chkbox_idx)
        return idxs


    @selected_choices_idxs.setter
    def selected_choices_idxs(self, selected_choices_idxs):

        old_is_selection_changed_event_active = self._is_selection_changed_event_active
        self._is_selection_changed_event_active = False

        for choice_idx in range(len(self.choices)):
            if choice_idx in selected_choices_idxs:
                self.choice_checkboxes[choice_idx].value = True
            else:
                self.choice_checkboxes[choice_idx].value = False

        self._is_selection_changed_event_active = old_is_selection_changed_event_active
        self._call_selection_changed_event()


    @property
    def selected_choices_inds(self):
        return [chkbox.value for chkbox in self.choice_checkboxes]


    @selected_choices_inds.setter
    def selected_choices_inds(self, selected_choices_inds):

        old_is_selection_changed_event_active = self._is_selection_changed_event_active
        self._is_selection_changed_event_active = False

        for choice_idx, is_selected in enumerate(selected_choices_inds):
            self.choice_checkboxes[choice_idx].value = is_selected

        self._is_selection_changed_event_active = old_is_selection_changed_event_active
        self._call_selection_changed_event()


    def on_selection_changed(self, handler):
        '''
        Register an event handler for changes of the selected choices.
        The handler receives a dict with information about the event.
        '''
        self._on_selection_changed_event_handlers.append(handler)


    def _update_titel(self):

        if self.config.title in ['SELECTED_CHOICES', 'TITLE_LABELS']:
            selected_choices_idxs = self.selected_choices_idxs

            if self.config.is_select_all_choice and self.select_all_checkbox.value == True:
                title = self.config.all_selected_title_label
            elif not selected_choices_idxs:
                title = self.config.none_selected_title_label
            else:
                if self.config.title == 'SELECTED_CHOICES':
                    labels = self.choices
                elif self.config.title == 'TITLE_LABELS':
                    labels = self.config.title_labels

                title = ''
                for idx, choice_idx in enumerate(selected_choices_idxs):
                    if idx > 0:
                        title += ', '
                    title += str(labels[choice_idx])

            self.accordion_widget.set_title(0, title)

    def _call_selection_changed_event(self):

        if self._is_selection_changed_event_active:

            self._update_titel()

            descr = {'name': 'selection_changed',
                     'new': {'value': False},
                     'owner': self,
                     'type': 'change'}

            for handler in self._on_selection_changed_event_handlers:
                handler(descr)


    def _on_select_all_checkbox_changed(self, event_descr):

        if self._is_on_select_all_checkbox_changed_active:

            # only react to changes of the value of a check box
            if event_descr['name'] == 'value' and event_descr['type'] == 'change':

                old_state = self._is_on_checkbox_changed_active
                self._is_on_checkbox_changed_active = False

                old_is_on_select_none_checkbox_changed_active = self._is_on_select_none_checkbox_changed_active
                self._is_on_select_none_checkbox_changed_active = False

                for chkbox in self.choice_checkboxes:
                    chkbox.value = event_descr['new']

                if self.config.is_select_none_choice:
                    self.select_none_checkbox.value = not event_descr['new']

                self._is_on_select_none_checkbox_changed_active = old_is_on_select_none_checkbox_changed_active
                self._is_on_checkbox_changed_active = old_state

                # call event, that the selection changed
                self._call_selection_changed_event()


    def _on_select_none_checkbox_changed(self, event_descr):

        if self._is_on_select_none_checkbox_changed_active:

            # only react to changes of the value of a check box
            if event_descr['name'] == 'value' and event_descr['type'] == 'change':

                old_state = self._is_on_checkbox_changed_active
                self._is_on_checkbox_changed_active = False

                old_is_on_select_all_checkbox_changed_active = self._is_on_select_all_checkbox_changed_active
                self._is_on_select_all_checkbox_changed_active = False

                for chkbox in self.choice_checkboxes:
                    chkbox.value = not event_descr['new']

                if self.config.is_select_all_choice:
                    self.select_all_checkbox.value = not event_descr['new']

                self._is_on_select_all_checkbox_changed_active = old_is_on_select_all_checkbox_changed_active
                self._is_on_checkbox_changed_active = old_state

                # call event, that the selection changed
                self._call_selection_changed_event()


    def _on_checkbox_changed(self, event_descr):

        if self._is_on_checkbox_changed_active:

            # only react to changes of the value of a check box
            if event_descr['name'] == 'value' and event_descr['type'] == 'change':

                # deactivate the event for "select all" checkbox
                # to not call this event again
                old_is_on_select_all_checkbox_changed_active = self._is_on_select_all_checkbox_changed_active
                self._is_on_select_all_checkbox_changed_active = False

                old_is_on_select_none_checkbox_changed_active = self._is_on_select_none_checkbox_changed_active
                self._is_on_select_none_checkbox_changed_active = False

                # all checkbox
                if event_descr['new'] == False and self.config.is_select_all_choice:
                    self.select_all_checkbox.value = False

                elif event_descr['new'] == True and self.config.is_select_all_choice:

                    # check if all choices are selected, if yes, then also activate the "select all" option
                    is_all_selected = True
                    for chkbox in self.choice_checkboxes:
                        if chkbox.value == False:
                            is_all_selected = False
                            break

                    if is_all_selected:
                        self.select_all_checkbox.value = True
                        # if self.config.is_select_none_choice:
                        #     self.select_none_checkbox.value = False

                # none checkbox
                if event_descr['new'] == True and self.config.is_select_none_choice:
                    self.select_none_checkbox.value = False

                elif event_descr['new'] == False and self.config.is_select_none_choice:

                    # check if no choices are selected, if yes, then also activate the "select none" option
                    is_none_selected = True
                    for chkbox in self.choice_checkboxes:
                        if chkbox.value == True:
                            is_none_selected = False
                            break

                    if is_none_selected:
                        self.select_none_checkbox.value = True
                        # if self.config.is_select_all_choice:
                        #     self.select_all_checkbox.value = False

                self._is_on_select_all_checkbox_changed_active = old_is_on_select_all_checkbox_changed_active
                self._is_on_select_none_checkbox_changed_active = old_is_on_select_none_checkbox_changed_active

                # call event, that the selection changed
                self._call_selection_changed_event()
