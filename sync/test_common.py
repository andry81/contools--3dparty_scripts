#!/usr/bin/env python

import unittest
import common

class Test_3dparty(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local_base_path = '/cygdrive/c/' if common.UseBundledRsync else '/c/'
        cls.folder = '3dparty/vc14_x64'
        cls.base_command = 'rsync --log-file=rsync.log --size-only -rvzz --delete-after'

    def test_3dparty_from(self):
        folder = Test_3dparty.folder
        base_command, remote_path, local_path = common.syncCommand(Test_3dparty.folder, silent=True)
        self.assertEqual(Test_3dparty.base_command, ' '.join(base_command))
        self.assertEqual(common.ServerIp + '::storage/' + folder + '/', remote_path)
        self.assertEqual(Test_3dparty.local_base_path + folder + '/', local_path)

    def test_3dparty_to(self):
        folder = Test_3dparty.folder
        base_command, remote_path, local_path = common.syncCommand(Test_3dparty.folder, readonly=False, silent=True)
        self.assertEqual(Test_3dparty.base_command, ' '.join(base_command))
        self.assertEqual(common.ServerRWUser + '@' + common.ServerIp + '::storage-rw/' + folder + '/', remote_path)
        self.assertEqual(Test_3dparty.local_base_path + folder + '/', local_path)

if __name__ == '__main__':
    unittest.main()

