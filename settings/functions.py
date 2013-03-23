import os

def get_cfg_setting(path, setting):
    """
    Search through a .cfg file for a given setting. Return it as a string.

    Settings should be of the form:
        settingname: value goes here
    """
    if os.path.exists(path):
        f = open(path, 'r')
        for line in f:
            line = line.strip()
            if line[0] != '#': # ignore comments
                splits = [ s.strip() for s in line.split(':', 1) ]
                if len(splits) >= 2 and splits[0] == setting:
                    return splits[1]
        f.close()
    return None

