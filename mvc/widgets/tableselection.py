"""tableselection.py -- High-level selection management. Subclasses defined in
the platform tableview modules provide the platform-specific methods used here.
"""

from contextlib import contextmanager

from mvc.errors import WidgetActionError, WidgetUsageError

class SelectionOwnerMixin(object):
    """Encapsulates the selection functionality of a TableView, for
    consistent behavior across platforms.

    Emits:
    :signal selection-changed: the selection has been changed
    :signal selection-invalid: the item selected can no longer be selected
    :signal deselected: all items have been deselected
    """
    def __init__(self):
        self._ignore_selection_changed = 0
        self._allow_multiple_select = None
        self.create_signal('selection-changed')
        self.create_signal('selection-invalid')
        self.create_signal('deselected')

    @property
    def allow_multiple_select(self):
        """Return whether the widget allows multiple selection."""
        if self._allow_multiple_select is None:
            self._allow_multiple_select = self._get_allow_multiple_select()
        return self._allow_multiple_select

    @allow_multiple_select.setter
    def allow_multiple_select(self, allow):
        """Set whether to allow multiple selection; this method is expected
        always to work.
        """
        if self._allow_multiple_select != allow:
            self._set_allow_multiple_select(allow)
            self._allow_multiple_select = allow

    @property
    def num_rows_selected(self):
        """Override on platforms with a way to count rows without having to
        retrieve them.
        """
        if self.allow_multiple_select:
            return len(self._get_selected_iters())
        else:
            return int(self._get_selected_iter() is not None)

    def select(self, iter_, signal=False):
        """Try to select an iter.

        :raises WidgetActionError: iter does not exist or is not selectable
        """
        self.select_iters((iter_,), signal)

    def select_iters(self, iters, signal=False):
        """Try to select multiple iters (signaling at most once).

        :raises WidgetActionError: iter does not exist or is not selectable
        """
        with self._ignoring_changes(not signal):
            for iter_ in iters:
                self._select(iter_)
        if not all(self._is_selected(iter_) for iter_ in iters):
            raise WidgetActionError("the specified iter cannot be selected")

    def is_selected(self, iter_):
        """Test if an iter is selected"""
        return self._is_selected(iter_)

    def unselect(self, iter_):
        """Unselect an Iter. Fails silently if the Iter is not selected.
        """
        self._validate_iter(iter_)
        with self._ignoring_changes():
            self._unselect(iter_)

    def unselect_iters(self, iters):
        """Unselect iters. Fails silently if the iters are not selected."""
        with self._ignoring_changes():
            for iter_ in iters:
                self.unselect(iter_)

    def unselect_all(self, signal=True):
        """Unselect all. emits only the 'deselected' signal."""
        with self._ignoring_changes():
            self._unselect_all()
            if signal:
                self.emit('deselected')

    def on_selection_changed(self, _widget_or_notification):
        """When we receive a selection-changed signal, we forward it if we're
        not in a 'with _ignoring_changes' block. Selection-changed
        handlers are run in an ignoring block, and anything that changes the
        selection to reflect the current state.
        """
        # don't bother sending out a second selection-changed signal if
        # the handler changes the selection (#15767)
        if not self._ignore_selection_changed:
            with self._ignoring_changes():
                self.emit('selection-changed')

    def get_selection_as_strings(self):
        """Returns the current selection as a list of strings.
        """
        return [self._iter_to_string(iter_) for iter_ in self.get_selection()]

    def set_selection_as_strings(self, selected):
        """Given a list of selection strings, selects each Iter represented by
        the strings.

        Raises WidgetActionError upon failure.
        """
        # iter may not be destringable (yet) - bounds error
        # destringed iter not selectable if parent isn't open (yet)
        self.set_selection(self._iter_from_string(sel) for sel in selected)

    def get_cursor(self):
        """Get the location of the keyboard cursor for the tableview.

        Returns a string that represents the row that the keyboard cursor is
        on.
        """

    def set_cursor(self, location):
        """Set the location of the keyboard cursor for the tableview.

        :param location: return value from a call to get_cursor()

        Raises WidgetActionError upon failure.
        """

    def get_selection(self):
        """Returns a list of GTK Iters. Works regardless of whether multiple
        selection is enabled.
        """
        return self._get_selected_iters()

    def get_selected(self):
        """Return the single selected item.
        
        :raises WidgetUsageError: multiple selection is enabled
        """
        if self.allow_multiple_select:
            raise WidgetUsageError("table allows multiple selection")
        return self._get_selected_iter()

    def _validate_iter(self, iter_):
        """Check whether an iter is valid.

        :raises WidgetDomainError: the iter is not valid
        :raises WidgetActionError: there is no model right now
        """

    @contextmanager
    def _ignoring_changes(self, ignoring=True):
        """Use this with with to prevent sending signals when we're changing
        our own selection; that way, when we get a signal, we know it's
        something important.
        """
        if ignoring:
            self._ignore_selection_changed += 1
        try:
            yield
        finally:
            if ignoring:
                self._ignore_selection_changed -= 1

    @contextmanager
    def preserving_selection(self):
        """Prevent selection changes in a block from having any effect or
        sticking - no signals will be sent, and the selection will be restored
        to its original value when the block exits.
        """
        iters = self._get_selected_iters()
        with self._ignoring_changes():
            try:
                yield
            finally:
                self.set_selection(iters)

    def set_selection(self, iters, signal=False):
        """Set the selection to the given iters, replacing any previous
        selection and signaling at most once.
        """
        self.unselect_all(signal=False)
        for iter_ in iters:
            self.select(iter_, signal=False)
        if signal: self.emit('selection-changed')
