'''
Created on Feb 24, 2018

@author: brian
'''

import logging, io, os, pickle

from envisage.ui.tasks.api import TasksApplication
from envisage.ui.tasks.tasks_application import TasksApplicationState
from pyface.api import error
from pyface.tasks.api import TaskWindowLayout
from traits.api import Bool, Instance, List, Property, Str, Any

logger = logging.getLogger(__name__)

from dptrp1.gui.preferences import Preferences


# Enthought library imports.
from pyface.api import GUI
from pyface.tasks.api import TaskWindow

from dptrp1.gui.gui_task import GUITask

class DPTApplication(TasksApplication):

    # The application's globally unique identifier.
    id = 'dptrp1.app'

    # The application's user-visible name.
    name = 'DPT-RP1 Manager'

    # The default window-level layout for the application.
    default_layout = List(TaskWindowLayout)
 
 
    # Whether to restore the previous application-level layout when the
    # applicaton is started.
    always_use_default_layout = Property(Bool)

    preferences_helper = Instance(Preferences)

    ###########################################################################
    # Private interface.
    ###########################################################################
     
#     def _load_state(self):
#         """ 
#         Loads saved application state, if possible.  Overload the envisage-
#         defined one to fix a py3k bug and increment the TasksApplicationState
#         version.
#         
#         """
#         state = TasksApplicationState(version = 1)
#         filename = os.path.join(self.state_location, 'application_memento')
#         if os.path.exists(filename):
#             # Attempt to unpickle the saved application state.
#             try:
#                 with open(filename, 'rb') as f:
#                     restored_state = pickle.load(f)
#                 if state.version == restored_state.version:
#                     state = restored_state
#                 else:
#                     logger.warn('Discarding outdated application layout')
#             except:
#                 # If anything goes wrong, log the error and continue.
#                 logger.exception('Had a problem restoring application layout from %s',
#                                  filename)
#                  
#         self._state = state
     
    #### Trait initializers ###################################################

    def _default_layout_default(self):
        active_task = self.preferences_helper.default_task
        tasks = [ factory.id for factory in self.task_factories ]
        return [ TaskWindowLayout(*tasks,
                                  active_task = active_task,
                                  size = (800, 600)) ]

    def _preferences_helper_default(self):
        return Preferences(preferences = self.preferences)

    #### Trait property getter/setters ########################################
 
    #### Trait property getter/setters ########################################
 
    def _get_always_use_default_layout(self):
        return self.preferences_helper.always_use_default_layout


def main(argv):
    
    logging.getLogger().setLevel(logging.DEBUG)
    
    ## send the log to STDERR
    try:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(name)s:%(message)s"))
        logging.getLogger().addHandler(console_handler)
    except:
        # if there's no console, this fails
        pass

    
    from envisage.core_plugin import CorePlugin
    from envisage.ui.tasks.tasks_plugin import TasksPlugin
    from dptrp1.gui.gui_task import GUITaskPlugin
    
    app = DPTApplication(plugins = [CorePlugin(), TasksPlugin(), GUITaskPlugin()])
    app.run()

if __name__ == '__main__':
    import sys
    main(sys.argv)