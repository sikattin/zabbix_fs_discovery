#!/usr/bin/python

### fs_discovery.py ###
# Zabbix UserParameter Script
#   discover mounted point of file systems mounted on the disk device.
#   for Zabbix LLD
###

import os, sys, glob, json
import logging
import argparse

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def get_blkdevs():
    """return block device names on the system.

    Returns:
        [list]
    """
    result = list()

    devs = _find_blkdevs()
    for dev in devs:
        dev_name = os.path.basename(dev)
        dev_size = 0
        if not os.path.islink(dev):
            continue
        if not _is_real_blkdev(dev_name):
            continue

        dev_size_file = '{0}/size'.format(dev)
        if not os.path.exists(dev_size_file):
            continue

        with open(dev_size_file) as f:
            dev_size = f.readline()
        if dev_size == 0:
            continue
        result.append(dev_name)
    return result

def get_fs(devs):
    """return mount path of mounted file system

    Args:
        devs(list): block device names
    Returns:
        [list]: mount path of the file system 
    """
    result = list()
    device = ""
    mnt_point = ""

    with open('/proc/mounts') as f:
        for line in f:
            split_words = line.split()
            device = os.path.basename(split_words[0].rstrip())
            mnt_point = split_words[1].rstrip()
            map(lambda x: result.append(mnt_point) if device.startswith(x) else None, devs)
    return result

def _find_blkdevs():
    """find block devices
    
    Returns:
        [list]: block devices list
    """
    return glob.glob('/sys/block/*')

def _is_real_blkdev(name):
    """checking that name is real block device or not
    
    Args:
        name (str): device file name
    """
    path = "/sys/block/{0}/device".format(name)
    if os.path.exists(path) and os.path.islink(path):
        return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action="store_true", help="enable debug mode")
    args = parser.parse_args()
    opt_dbg = args.debug
    if opt_dbg:
        logger.removeHandler(ch)
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)

    result = {"data": []}
    block_devs = get_blkdevs()
    logger.debug("block devices: %s" % block_devs)
    fss = get_fs(block_devs)
    logger.debug("file systems: %s" % fss)
    [result['data'].append({"{#FSNAME}": str(fs)}) for fs in fss]
    print(json.dumps(result, sort_keys=True, indent=4))
