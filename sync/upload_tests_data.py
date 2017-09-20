#!/usr/bin/env python

import common

if __name__ == '__main__':
    common.syncFolder('tests_data', backward=True)
    input('Press <ENTER> to quit')
