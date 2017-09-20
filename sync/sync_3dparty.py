#!/usr/bin/env python

import common
import sys

if __name__ == '__main__':
    subfolders = sys.argv[1:]
    if not subfolders:
        print('Unable to sync anything! Please, provide 3dparty subfolders list to fetch')
    else:
        common.syncFolders(['3dparty/' + subfolder for subfolder in subfolders])
    input('Press <ENTER> to quit')
