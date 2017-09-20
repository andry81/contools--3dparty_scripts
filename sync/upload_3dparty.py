#!/usr/bin/env python

import common
import sys

if __name__ == '__main__':
    subfolders = sys.argv[1:]
    if not subfolders:
        print('Unable to upload anything! Please, provide 3dparty subfolders list to upload')
    else:
        common.syncFolders(['3dparty/' + subfolder for subfolder in subfolders], backward=True)
    input('Press <ENTER> to quit')
