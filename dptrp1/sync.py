'''
Created on Apr 28, 2018

@author: brian
'''
import os, pickle, time, pytz
from datetime import datetime
from pathlib import Path

def sync(dp, path, resolve = "time"):
    """
    Synchronize a directory on the local host with the DPT-RP1.
    
    The first time the device is synchronized, the local directory must be
    empty.
    
    Arguments:
    
        dp : instance of DigitalPaper
            The DigitalPaper instance must already be connected to the 
            remote device.
            
        resolve : "time", "local", "remote" or callable
            What do we do in the case of a conflict?  A conflict arises if
            a file was created in both the local folder and remote device
            with the same name, or if an existing file is changed on both
            sides before synchronizing.  The question is, which version do
            we keep?
            
            If `resolve` is set to "time", then keep the one that was updated
            the most recently.  The DPT-RP1's clock is updated each time
            it connects, so it should be pretty accurate.
            
            If `resolve` is set to "local", then always keep the local
            (computer's) copy.  If `resolve` is "remote", then always
            keep the remote (DPT-RP1's) copy.
            
            Finally, `resolve` can be a callable.  If it is, then it must
            take a DigitalPaper instance and a relative filename, and
            return "local" or "remote" (depending on which we should keep.)
            
            Because the callable takes a DigitalPaper instance, it could
            even do something fancy like download the file, merge them,
            save the merged version to the "local" file, and return "local".
            Or, it could ask the user which they would rather keep.
    """
    
    # check that either the directory is empty, or has some history data
    base_path = Path(path)
    
    if not base_path.exists():
        raise RuntimeError("Sync patn {} doesn't exist".format(base_path))
    
    if not base_path.is_dir():
        raise RuntimeError("Sync path {} isn't a directory".format(base_path))
    
    history_path = base_path / ".history"
    
    if history_path.exists():
        with open(history_path, 'r') as f:
            local_history, remote_history = pickle.load(f)
    else:
#         if os.listdir(base_path) is not []:
#             raise RuntimeError("Sync path {} isn't empty, but doesn't have any history")
        local_history = {}
        remote_history = {}
        
    # the history is a dictionary representing the state of the device
    # the last time we sync'd.
    # keys: Path objects representing files
    # entries: modification time (on the device), or None if it's a directory

    local_changes = {}
    for p in base_path.iterdir():
        print(p)
        modtime = datetime.utcfromtimestamp(os.path.getmtime(p))
        modtime = pytz.utc.localize(modtime)
        print(modtime)
        
    remote_tz = dp.get_configuration()['timezone']['value']
    remote_tz = pytz.timezone(remote_tz)
    print(remote_tz)
    remote_files = dp.list_documents()
    f = [x for x in remote_files if x['entry_path'] == 'Document/hello.pdf']
    f = f[0]
    print(f)
    
    
    filedate = f['modified_date']
    dt = datetime.strptime(filedate, "%Y-%m-%dT%H:%M:%SZ")
    dt = remote_tz.localize(dt)  
    print(dt)
    print(dt - modtime)
#     dt.tzinfo = remote_tz
#     print(remote_files[0])
#     print(remote_files)
#         print(datetime.fromtimestamp(modtime))
#         if p in local_history:

        
#     n = {}
#     
#     remote_documents = dp.list_documents()
        
        
    
    
    
    