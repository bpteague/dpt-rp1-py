'''
Created on Feb 24, 2018

@author: brian
'''

from traits.api import HasTraits, Str, List, CBool, CInt, Enum, Either, Instance

class File(HasTraits):
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

class Folder(HasTraits):
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

    

class DPTModel(HasTraits):
    root = Instance(Folder)