'''
Created on Feb 24, 2018

@author: brian
'''

# Standard library imports.
import os.path

# Enthought library imports.
from pyface.api import PythonEditor
from pyface.tasks.api import TaskPane, TraitsDockPane
from traits.api import Event, File, Instance, List, Str
from traitsui.api import View, Item, FileEditor, TreeEditor

from dptrp1.gui.dpt_model import DPTModel

class DPTPane(TaskPane):
    """ A wrapper around the Pyface Python editor.
    """

    #### TaskPane interface ###################################################

    id = 'dpt_rp1.dpt_pane'
    name = 'DPT-RP1 contents'

    #### PythonEditorPane interface ###########################################

    model = Instance(DPTModel)

    ###########################################################################
    # 'ITaskPane' interface.
    ###########################################################################

    def create(self, parent):
        self.control = self.model.edit_traits(kind = 'subpanel', 
                                              parent = parent,
                                              handler = self.task).control

    def destroy(self):
        self.control = None