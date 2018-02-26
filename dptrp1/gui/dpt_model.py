'''
Created on Feb 24, 2018

@author: brian
'''

from traits.api import HasTraits, Str, List, CBool, CInt, Enum, Either, Instance, Property
from traitsui.api import View, Item, TreeEditor, TreeNode, Menu, Action
from traitsui.qt4.tree_editor import NewAction, RenameAction, DeleteAction
from pyface.tasks.action.api import TaskAction

class File(HasTraits):
    name = Property
    entry_id = Str
    document_source = Str
    entry_type = Enum(['document', 'folder'])
    total_page = CInt
    mime_type = Str
    author = Str
    entry_name = Str
    entry_path = Str
    reading_date = Str
    file_size = CInt
    current_page = CInt
    created_date = Str
    title = Str
    modified_date = Str
    document_type = Str
    parent_folder_id = Str
    is_new = CBool
    file_revision = Str
    
    parent_folder = Instance("dptrp1.gui.dpt_model.Folder")
    
    def _get_name(self):
        return self.entry_name

class Folder(HasTraits):
    name = Property
    created_date = Str
    document_source = Str
    entry_name = Str
    entry_id = Str
    entry_type = Enum(['document', 'folder'])
    entry_path = Str
    parent_folder_id = Str
    is_new = CBool
    
    parent_folder = Instance("dptrp1.gui.dpt_model.Folder")
    files = List(Either(Instance("dptrp1.gui.dpt_model.File"), Instance("dptrp1.gui.dpt_model.Folder")))
    
    def _get_name(self):
        return self.entry_name
    
DeleteAction = Action(name = 'Delete',
                      action = 'handler._delete_nodes(editor)')

UploadAction = Action(name = 'Upload',
                      action = 'handler._upload_files(editor)')

DownloadAction = Action(name = 'Download',
                        action = 'handler._download_files(editor)')

SyncAction = Action(name = "Synchronize",
                    action = 'handler._sync_folder(editor)')

class DPTModel(HasTraits):
    root = Instance(Folder, ())
    
    view = View(Item('root',
                     editor = TreeEditor(
                                    nodes = [
                                        TreeNode(node_for = [Folder],
                                                 auto_open = True,
                                                 label = 'entry_name',
                                                 children = 'files',
                                                 view = View(),
                                                 add = [Folder],
                                                 menu = Menu(NewAction,
                                                             DeleteAction,
                                                             RenameAction,
                                                             UploadAction,
                                                             DownloadAction,
                                                             SyncAction) ),
        
                                        TreeNode(node_for = [File],
                                                 label = 'entry_name',
                                                 view = View(),
                                                 menu = Menu(DeleteAction,
                                                             RenameAction,
                                                             DownloadAction))],
                                    selection_mode = 'extended'),
                     show_label = False))
    
