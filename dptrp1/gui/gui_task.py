'''
Created on Feb 24, 2018

@author: brian
'''

import os, logging, requests

# Enthought library imports.
from envisage.api import Plugin, contributes_to
from envisage.ui.tasks.api import TaskFactory
from envisage.ui.tasks.action.preferences_action import PreferencesAction

from pyface.tasks.api import Task
from pyface.tasks.action.api import SMenuBar, SMenu, SToolBar, TaskAction
from pyface.api import error, FileDialog, OK, NO, confirm
from traits.api import Instance
from traitsui.api import Controller

from dptrp1.gui.gui_panes import DPTPane
from dptrp1.gui.dpt_model import DPTModel, File, Folder
from dptrp1.api import DigitalPaper

# Local imports.
# from example_panes import PythonEditorPane, PythonScriptBrowserPane


class GUITask(Task, Controller):
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
    

    def create_central_pane(self):
        """ Create the central pane: the script editor.
        """
        return DPTPane(model = self.model)

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
                
        
    def _delete_nodes(self, editor):
        selected = editor.selected

        if len(selected) == 1:
            ret = confirm(
                    None, 
                    "Are you sure you want to delete {}?".format(selected[0].name),
                    title = "Delete?",
                    default = NO)
            if ret == NO:
                return

        else:
            parent = selected[0].parent_folder_id

            for s in selected:
                if isinstance(s, Folder):
                    error(None, "Can only remove one folder at a time.")
                    return

                if s.parent_folder_id != parent:
                    error(None, "Can only remove multiple documents in the same folder.")
                    return

            ret = confirm(None,
                    "Are you sure you want to delete {} documents?"
                    .format(len(selected)),
                    title = "Delete?",
                    default = NO)

            if ret == NO:
                return

        parent = selected[0].parent_folder

        for s in selected:
            if isinstance(s, Folder):
                self.dp.delete_folder(s.entry_id)
            else: #file
                self.dp.delete(s.entry_id)
            
            # remove from model -- which removes it from the tree
            # TODO - this raises an exception when removing a folder.
            # possibly because we're removing the object from a
            # handler on the object itself.
            
            parent.files.remove(s)
        

    def _upload_files(self, editor):
        
        selected = editor.selected[0]

        d = FileDialog(action = 'open files',
                       wildcard = '"PDF files (*.pdf)|*.pdf|"',
                       style = 'modal')
        d.open()
        
        if d.return_code != OK:
            return
        
        for path in d.paths:
            _, filename = os.path.split(path)
            remote_folder = selected.entry_path
            remote_path = remote_folder + '/' + filename

            try:
                remote_id = self.dp.get_document_id(remote_path)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code != 404:
                    raise e
                remote_id = None
            
            if remote_id is not None:
                ret = confirm(
                        None, 
                        "{} already exists!  Overwrite?".format(remote_path),
                        title = "Overwrite?",
                        default = NO)
                if ret == NO:
                    continue
                
            logging.debug("Uploading {}".format(remote_path))
            
            with open(path, 'rb') as fh:
                remote_id = self.dp.upload(selected.entry_id, filename, fh)
            
            remote_file_info = self.dp.get_document_info(remote_id)
            selected.files.append(File(**remote_file_info))

    def _download_files(self, editor):
        pass

    def _sync_folder(self, editor):
        pass
                
            

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
