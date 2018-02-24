'''
Created on Feb 24, 2018

@author: brian
'''

import os
import requests

# Enthought library imports.
from envisage.api import Plugin, ExtensionPoint, contributes_to
from envisage.ui.tasks.api import TaskFactory
from envisage.ui.tasks.action.preferences_action import PreferencesAction

from pyface.tasks.api import Task, TaskLayout, PaneItem
from pyface.tasks.action.api import DockPaneToggleGroup, SMenuBar, \
    SMenu, SToolBar, TaskAction
from pyface.api import error, ConfirmationDialog, FileDialog, \
    ImageResource, YES, OK, CANCEL
from traits.api import on_trait_change, Instance

from dptrp1.gui.gui_panes import DPTPane
from dptrp1.gui.dpt_model import DPTModel, File, Folder
from dptrp1.api import DigitalPaper

# Local imports.
# from example_panes import PythonEditorPane, PythonScriptBrowserPane


class GUITask(Task):
    """ A simple task for editing Python code.
    """

    #### Task interface #######################################################

    id = 'dptrp1.gui_task'
    name = 'DPT-RP1 GUI'
    
    dp = Instance(DigitalPaper)
    model = Instance(DPTModel, ())

    #default_layout = TaskLayout(
    #    left=PaneItem('example.python_script_browser_pane'))

    menu_bar = SMenuBar(SMenu(TaskAction(name='Connect...', method='connect',
                                         accelerator='Ctrl+O'),
                              PreferencesAction(name = "Register..."),
                              id='File', name='&File'))
#                         SMenu(DockPaneToggleGroup(),
#                               id='View', name='&View'))

    tool_bars = [ SToolBar(TaskAction(method='connect',
                                      name = 'Connect...',
                                      tooltip='Connect to the DPT-RP1'),
#                                       image=ImageResource('document_open')),
                           PreferencesAction(name = "Register..."))]
    
    

    ###########################################################################
    # 'Task' interface.
    ###########################################################################

#     def _default_layout_default(self):
#         return TaskLayout(
#             left=PaneItem('example.python_script_browser_pane'))

#     def activated(self):
#         """ Overriden to set the window's title.
#         """
#         filename = self.window.central_pane.editor.path
#         self.window.title = filename if filename else 'Untitled'

    def create_central_pane(self):
        """ Create the central pane: the script editor.
        """
        return DPTPane(model = self.model)

#     def create_dock_panes(self):
#         """ Create the file browser and connect to its double click event.
#         """
#         browser = PythonScriptBrowserPane()
#         handler = lambda: self._open_file(browser.selected_file)
#         browser.on_trait_change(handler, 'activated')
#         return [ browser ]

    ###########################################################################
    # 'ExampleTask' interface.
    ###########################################################################

    def connect(self):
        addr = self.application.preferences_helper.addr
        client_id = self.application.preferences_helper.client_id
        key = self.application.preferences_helper.key
        
        try:
            self.dp = DigitalPaper(addr = addr)
            self.dp.authenticate(client_id, key)
        except requests.exceptions.ConnectionError as e:
            error(None, "Could not connect to DPT-RP1 at {}: {}".format(addr, str(e)))
        except requests.exceptions.HTTPError as e:
            error(None, "Error authenticating with DPT-RP1 at {}: {}".format(addr, str(e)))
        except Exception as e:
            error(None, "Other error connecting to DPT-RP1: {}".format(str(e)))
            
        files = []
        folders = [Folder(entry_id = "root",
                          entry_name = "Document")]
            
        docs = self.dp.list_documents()
        for d in docs:
            if d['entry_type'] == 'folder':
                f = Folder(**d)
                folders.append(f)
            else:
                f = File(**d)
                files.append(f)
                
        for file in files:
            folder = next(f for f in folders if f.entry_id == file.parent_folder_id)
            folder.files.append(file)
            file.parent_folder = folder
            
        for folder in folders:
            if folder.entry_id == 'root':
                continue
            parent_folder = next(f for f in folders if f.entry_id == folder.parent_folder_id)
            parent_folder.files.append(folder)
            folder.parent_folder = parent_folder
            
        self.model.root = folders[0]
                
        
                
            
        
#         """ Shows a dialog to open a file.
#         """
#         dialog = FileDialog(parent=self.window.control, wildcard='*.py')
#         if dialog.open() == OK:
#             self._open_file(dialog.path)

    def register(self):
        pass
#         """ Attempts to save the current file, prompting for a path if
#             necessary. Returns whether the file was saved.
#         """
#         editor = self.window.central_pane.editor
#         try:
#             editor.save()
#         except IOError:
#             # If you are trying to save to a file that doesn't exist, open up a
#             # FileDialog with a 'save as' action.
#             dialog = FileDialog(parent=self.window.control,
#                                 action='save as', wildcard='*.py')
#             if dialog.open() == OK:
#                 editor.save(dialog.path)
#             else:
#                 return False
#         return True

    ###########################################################################
    # Protected interface.
    ###########################################################################

#     def _open_file(self, filename):
#         """ Opens the file at the specified path in the editor.
#         """
#         if self._prompt_for_save():
#             self.window.central_pane.editor.path = filename
#             self.activated()
# 
#     def _prompt_for_save(self):
#         """ Prompts the user to save if necessary. Returns whether the dialog
#             was cancelled.
#         """
#         if self.window.central_pane.editor.dirty:
#             message = 'The current file has unsaved changes. ' \
#                       'Do you want to save your changes?'
#             dialog = ConfirmationDialog(parent=self.window.control,
#                                         message=message, cancel=True,
#                                         default=CANCEL, title='Save Changes?')
#             result = dialog.open()
#             if result == CANCEL:
#                 return False
#             elif result == YES:
#                 if not self.save():
#                     return self._prompt_for_save()
#         return True
# 
#     @on_trait_change('window:closing')
#     def _prompt_on_close(self, event):
#         """ Prompt the user to save when exiting.
#         """
#         if not self._prompt_for_save():
#             event.veto = True

class GUITaskPlugin(Plugin):
    """
    An Envisage plugin wrapping FlowTask
    """

    # Extension point IDs.
    PREFERENCES       = 'envisage.preferences'
    PREFERENCES_PANES = 'envisage.ui.tasks.preferences_panes'
    TASKS             = 'envisage.ui.tasks.tasks'

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = 'dptrp1.gui'

    # The plugin's name (suitable for displaying to the user).
    name = 'DPT-RP1 Manager'

    ###########################################################################
    # Protected interface.
    ###########################################################################

    @contributes_to(PREFERENCES)
    def _get_preferences(self):
        filename = os.path.join(os.path.dirname(__file__), 'preferences.ini')
        return [ 'file://' + filename ]
    
    @contributes_to(PREFERENCES_PANES)
    def _get_preferences_panes(self):
        from .preferences import PreferencesPane
        return [PreferencesPane]

    @contributes_to(TASKS)
    def _get_tasks(self):
        return [TaskFactory(id = 'edu.mit.synbio.cytoflowgui.flow_task',
                            name = 'Cytometry analysis',
                            factory = lambda **x: GUITask(application = self.application, **x))]
