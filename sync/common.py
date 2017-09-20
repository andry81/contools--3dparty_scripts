#!/usr/bin/env python

from distutils import spawn
from sys import version_info
import subprocess
import re, os, sys, glob, errno
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

script_dir = os.path.dirname(os.path.realpath(__file__))

ServerIp = '192.168.0.100'
ServerRWUser = 'user-rw'
ServerRWPass = 'user-rw-pass'

BundledRsyncDir = os.path.join(script_dir, 'cwRsync')
UseBundledRsync = not spawn.find_executable('rsync')

DeleteAfter = False

def getUserInput(message, defaultValue = ''):
    messageToAsk = message % defaultValue if defaultValue else message
    userInput = input(messageToAsk) if version_info[0] > 2 else raw_input(messageToAsk)
    if (not userInput): userInput = defaultValue
    return userInput.rstrip('\/')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def askLocalBasePath(basePath, initialBasePath=str()):
    while True:
        userPath = getUserInput('\t[' + basePath + '] local path [%s]: ', initialBasePath)
        userPath = os.path.abspath(os.path.expanduser(os.path.expandvars(userPath)))

        if not userPath or userPath.startswith(script_dir):
            print('Invalid path [{0}]! Please, choose another one...'.format(userPath))
            continue

        return userPath

def syncCommand(folder, readonly=True, silent=False):
    components = list(filter(len, folder.split('/', maxsplit=1)))
    basePath, subPath = components[0], components[1] if len(components) > 1 else ''

    config = ConfigParser()
    basePathSetting = basePath.lower() + '_root'

    # get cached folder setting
    try:
        config.read('_env.ini')
        localBasePath = config.get('LocalPath', basePathSetting)
    except:
        pass

    # check path and if necessary set to default path depending python being run: cygwin, msys or native
    if not localBasePath or not os.path.exists(localBasePath):
        for p in ['/cygdrive/c/', '/cygdrive/d/', '/cygdrive/e/', '/c/', '/d/', '/e/', 'c:\\', 'd:\\', 'e:\\']:
            if os.path.exists(p):
                localBasePath = os.path.join(p, basePath)
                break

    # notify user and verify path validity
    if not silent:
        localBasePath = askLocalBasePath(basePath, localBasePath)

    localFullPath = os.path.join(localBasePath, subPath)
    print('\n(*) For sync folder [' + folder + '] using path:\n\t' + localFullPath + '\n')

    # bundled rsync expects cygwin style local path
    if UseBundledRsync:
        localFullPath = re.sub('^(|/)([a-zA-Z])(:|)/', '/cygdrive/\\2/', localFullPath.replace('\\', '/'))

    if not folder.endswith('/'): folder += '/'
    if not localFullPath.endswith('/'): localFullPath += '/'

    # write down path which intended to be used before actual sync
    if not silent:
        try:
            if not config.has_section('LocalPath'):
                config.add_section('LocalPath')
            config.set('LocalPath', basePathSetting, localBasePath)
            with open('_env.ini', 'w') as configFile:
                config.write(configFile)
        except Exception as e:
            print('(!) failed to write local path setting: ' + str(e))

    # sync subprocess command
    base_command = ['rsync', '--log-file=rsync.log', '-rvhzzct']

    global DeleteAfter
    if not silent:
        while (True):
            answer = getUserInput('(!) Delete all waste files in destination directory after sync? [' + ('%s/n' if DeleteAfter else 'y/%s') + ']: ', 'Y' if DeleteAfter else 'N')
            if answer.lower() == 'n':
                DeleteAfter = False
                break
            elif answer.lower() == 'y':
                DeleteAfter = True
                break
                
    if DeleteAfter:
        print('\n!!! WARNING WARNING WARNING !!! \nAll ***WASTE*** files in [' + localFullPath + '] directory will be DELETED!\n')
        base_command.append('--delete-after')

    remote_path = ('' if readonly else ServerRWUser + '@') + ServerIp + '::storage' + ('' if readonly else '-rw') + '/' + folder

    return base_command, remote_path, localFullPath

def syncFolder(folder, backward=False, silent=False):
    command, remote_path, local_path = syncCommand(folder, not backward, silent)
    if UseBundledRsync:
        command[0] = os.path.join(BundledRsyncDir, command[0])
    command.extend([local_path, remote_path] if backward else [remote_path, local_path])
    print('(*) Will execute:\n\t{}\n'.format(' '.join(command)))

    while (not silent and True):
        answer = getUserInput('Start sync process? [%s/n]: ', 'y'.upper())
        if answer.lower() == 'n':
            getUserInput('Aborted. Press any key to quit...')
            exit(0)
        elif answer.lower() == 'y':
            break

    # create full folders path before sync to check write access
    if sys.version_info[0] >= 3:
        os.makedirs(local_path, exist_ok=True)
    else:
        mkdir_p(local_path)

    try:
        print('---- Sync subprocess starting...')
        env = None
        if backward:
            env = dict(os.environ)
            env['RSYNC_PASSWORD'] = ServerRWPass
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        for line in proc.stdout:
            print(line.decode(), end='')
        ret = proc.wait()
        print('---- Sync subprocess ended [code: {}]'.format(ret))
    except Exception as err:
        print('---- Sync failed! Error:', err)
        raise

def syncFolders(folders, backward=False, silent=False):
    synched = set()
    for folder in folders:
        base_folder = folder.split('/', maxsplit=1)[0]
        print('-- Syncing folder [{}]...'.format(folder))
        syncFolder(folder, backward, silent if base_folder not in synched else True)
        synched.add(base_folder)
        print('-- Dir [{}] sync success'.format(folder))

def enterInput(msg):
    if sys.version_info[0] >= 3:
        return input(msg)
    else:
        return raw_input(msg)

if __name__ == '__main__':
    argv = sys.argv
    arg1 = argv[1] if len(argv) > 1 else ''
    if not arg1 or arg1 in [ '-h', '--help' ]:
        print('Usage:\n\t common.py -h \n\t common.py [TO|FROM] (TO) 3dparty/vc14_x86 3dparty/vc14_x64')
    else:
        backward = False
        if arg1 in ['TO', 'FROM']:
            backward = arg1 == 'FROM'
            del argv[1]
        folders = argv[1:]
        syncFolders(folders, backward=backward)

