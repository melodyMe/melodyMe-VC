"""``melodyMe.frontends.widgets.dialogs`` -- Dialog boxes for the Widget
frontend.

The difference between this module and rundialog.py is that rundialog
handles dialog boxes that are coming from the backend code.  This
model handles dialogs that we create from the frontend

One big difference is that we don't have to be as general about
dialogs, so they can present a somewhat nicer API.  One important
difference is that all of the dialogs run modally.
"""

from mvc.widgets import widgetset
from mvc.widgets import widgetutil

class DialogButton(object):
    def __init__(self, text):
        self._text = text
    def __eq__(self, other):
        return isinstance(other, DialogButton) and self.text == other.text
    def __str__(self):
        return "DialogButton(%r)" % self.text
    @property
    def text(self):
        return unicode(self._text)

BUTTON_OK = DialogButton("OK")
BUTTON_APPLY = DialogButton("Apply")
BUTTON_CLOSE = DialogButton("Close")
BUTTON_CANCEL = DialogButton("Cancel")
BUTTON_DONE = DialogButton("Done")
BUTTON_YES = DialogButton("Yes")
BUTTON_NO = DialogButton("No")
BUTTON_QUIT = DialogButton("Quit")
BUTTON_CONTINUE = DialogButton("Continue")
BUTTON_IGNORE = DialogButton("Ignore")
BUTTON_IMPORT_FILES = DialogButton("Import Files")
BUTTON_SUBMIT_REPORT = DialogButton("Submit Crash Report")
BUTTON_MIGRATE = DialogButton("Migrate")
BUTTON_DONT_MIGRATE = DialogButton("Don't Migrate")
BUTTON_DOWNLOAD = DialogButton("Download")
BUTTON_REMOVE_ENTRY = DialogButton("Remove Entry")
BUTTON_DELETE_FILE = DialogButton("Delete File")
BUTTON_DELETE_FILES = DialogButton("Delete Files")
BUTTON_KEEP_VIDEOS = DialogButton("Keep Videos")
BUTTON_DELETE_VIDEOS = DialogButton("Delete Videos")
BUTTON_CREATE = DialogButton("Create")
BUTTON_CREATE_FEED = DialogButton("Create Podcast")
BUTTON_CREATE_FOLDER = DialogButton("Create Folder")
BUTTON_CHOOSE_NEW_FOLDER = DialogButton("Choose New Folder")
BUTTON_ADD_FOLDER = DialogButton("Add Folder")
BUTTON_ADD = DialogButton("Add")
BUTTON_ADD_INTO_NEW_FOLDER = DialogButton("Add Into New Folder")
BUTTON_KEEP = DialogButton("Keep")
BUTTON_DELETE = DialogButton("Delete")
BUTTON_REMOVE = DialogButton("Remove")
BUTTON_NOT_NOW = DialogButton("Not Now")
BUTTON_CLOSE_TO_TRAY = DialogButton("Close to Tray")
BUTTON_LAUNCH_MIRO = DialogButton("Launch melodyMe")
BUTTON_DOWNLOAD_ANYWAY = DialogButton("Download Anyway")
BUTTON_OPEN_IN_EXTERNAL_BROWSER = DialogButton(
                                               "Open in External Browser")
BUTTON_DONT_INSTALL = DialogButton("Don't Install")
BUTTON_SUBSCRIBE = DialogButton("Subscribe")
BUTTON_STOP_WATCHING = DialogButton("Stop Watching")
BUTTON_RETRY = DialogButton("Retry")
BUTTON_START_FRESH = DialogButton("Start Fresh")
BUTTON_INCLUDE_DATABASE = DialogButton("Include Database")
BUTTON_DONT_INCLUDE_DATABASE = DialogButton(
                                            "Don't Include Database")

WARNING_MESSAGE = 0
INFO_MESSAGE = 1
CRITICAL_MESSAGE = 2


class ProgressDialog(widgetset.Dialog):
    def __init__(self, title):
        widgetset.Dialog.__init__(self, title, description='')
        self.progress_bar = widgetset.ProgressBar()
        self.label = widgetset.Label()
        self.label.set_size(1.2)
        self.vbox = widgetset.VBox(spacing=6)
        self.vbox.pack_end(widgetutil.align_center(self.label))
        self.vbox.pack_end(self.progress_bar)
        self.set_extra_widget(self.vbox)

    def update(self, description, progress):
        self.label.set_text(description)
        if progress >= 0:
            self.progress_bar.set_progress(progress)
            self.progress_bar.stop_pulsing()
        else:
            self.progress_bar.start_pulsing()

class DBUpgradeProgressDialog(widgetset.Dialog):
    def __init__(self, title, text):
        widgetset.Dialog.__init__(self, title)
        self.progress_bar = widgetset.ProgressBar()
        self.top_label = widgetset.Label()
        self.top_label.set_text(text)
        self.top_label.set_wrap(True)
        self.top_label.set_size_request(350, -1)
        self.label = widgetset.Label()
        self.vbox = widgetset.VBox(spacing=6)
        self.vbox.pack_end(widgetutil.align_center(self.label))
        self.vbox.pack_end(self.progress_bar)
        self.vbox.pack_end(widgetutil.pad(self.top_label, bottom=6))
        self.set_extra_widget(self.vbox)

    def update(self, stage, stage_progress, progress):
        self.label.set_text(stage)
        self.progress_bar.set_progress(progress)

def show_about():
    window = widgetset.AboutDialog()
    set_transient_for_main(window)
    try:
        window.run()
    finally:
        window.destroy()

def show_message(title, description, alert_type=INFO_MESSAGE,
        transient_for=None):
    """Display a message to the user and wait for them to click OK"""
    window = widgetset.AlertDialog(title, description, alert_type)
    _set_transient_for(window, transient_for)
    try:
        window.add_button(BUTTON_OK.text)
        window.run()
    finally:
        window.destroy()

def show_choice_dialog(title, description, choices, transient_for=None):
    """Display a message to the user and wait for them to choose an option.
    Returns the button object chosen."""
    window = widgetset.Dialog(title, description)
    try:
        for mem in choices:
            window.add_button(mem.text)
        response = window.run()
        return choices[response]
    finally:
        window.destroy()

def ask_for_string(title, description, initial_text=None, transient_for=None):
    """Ask the user to enter a string in a TextEntry box.

    description - textual description with newlines
    initial_text - None, string or callable to pre-populate the entry box

    Returns the value entered, or None if the user clicked cancel
    """
    window = widgetset.Dialog(title, description)
    try:
        window.add_button(BUTTON_OK.text)
        window.add_button(BUTTON_CANCEL.text)
        entry = widgetset.TextEntry()
        entry.set_activates_default(True)
        if initial_text:
            if callable(initial_text):
                initial_text = initial_text()
            entry.set_text(initial_text)
        window.set_extra_widget(entry)
        response = window.run()
        if response == 0:
            return entry.get_text()
        else:
            return None
    finally:
        window.destroy()

def ask_for_choice(title, description, choices):
    """Ask the user to enter a string in a TextEntry box.

    :param title: title for the window
    :param description: textual description with newlines
    :param choices: list of labels for choices
    Returns the index of the value chosen, or None if the user clicked cancel
    """
    window = widgetset.Dialog(title, description)
    try:
        window.add_button(BUTTON_OK.text)
        window.add_button(BUTTON_CANCEL.text)
        menu = widgetset.OptionMenu(choices)
        window.set_extra_widget(menu)
        response = window.run()
        if response == 0:
            return menu.get_selected()
        else:
            return None
    finally:
        window.destroy()

def ask_for_open_pathname(title, initial_filename=None, filters=[],
        transient_for=None, select_multiple=False):
    """Returns the file pathname or None.
    """
    window = widgetset.FileOpenDialog(title)
    _set_transient_for(window, transient_for)
    try:
        if initial_filename:
            window.set_filename(initial_filename)

        if filters:
            window.add_filters(filters)

        if select_multiple:
            window.set_select_multiple(select_multiple)

        response = window.run()
        if response == 0:
            if select_multiple:
                return window.get_filenames()
            else:
                return window.get_filename()
    finally:
        window.destroy()

def ask_for_save_pathname(title, initial_filename=None, transient_for=None):
    """Returns the file pathname or None.
    """
    window = widgetset.FileSaveDialog(title)
    _set_transient_for(window, transient_for)
    try:
        if initial_filename:
            window.set_filename(initial_filename)
        response = window.run()
        if response == 0:
            return window.get_filename()
    finally:
        window.destroy()

def ask_for_directory(title, initial_directory=None, transient_for=None):
    """Returns the directory pathname or None.
    """
    window = widgetset.DirectorySelectDialog(title)
    _set_transient_for(window, transient_for)
    try:
        if initial_directory:
            window.set_directory(initial_directory)

        response = window.run()
        if response == 0:
            return window.get_directory()
    finally:
        window.destroy()
