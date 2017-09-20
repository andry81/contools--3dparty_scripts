#!/usr/bin/env python

import common

if __name__ == '__main__':
    common.syncFolder('3dparty/build', backward=True)
    input('Press <ENTER> to quit')
