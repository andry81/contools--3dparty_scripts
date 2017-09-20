#!/usr/bin/env python

import common

if __name__ == '__main__':
    common.syncFolder('3dparty/vc14_x64', backward=True)
    input('Press <ENTER> to quit')
