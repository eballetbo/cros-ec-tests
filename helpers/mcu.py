#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fcntl
import os
from helpers.sysfs import *
from ctypes import *

EC_CMD_PROTO_VERSION    = 0x0000
EC_CMD_HELLO            = 0x0001
EC_CMD_GET_VERSION      = 0x0002
EC_CMD_GET_FEATURES     = 0x000D

EC_HOST_PARAM_SIZE      = 0xfc

EC_DEV_IOCXCMD          = 0xc014ec00  # _IOWR(EC_DEV_IOC, 0, struct cros_ec_command)

ECFEATURES              = -1
# Supported features
EC_FEATURE_LIMITED                          = 0
EC_FEATURE_FLASH                            = 1
EC_FEATURE_PWM_FAN                          = 2
EC_FEATURE_PWM_KEYB                         = 3
EC_FEATURE_LIGHTBAR                         = 4
EC_FEATURE_LED                              = 5
EC_FEATURE_MOTION_SENSE                     = 6
EC_FEATURE_KEYB                             = 7
EC_FEATURE_PSTORE                           = 8
EC_FEATURE_PORT80                           = 9
EC_FEATURE_THERMAL                          = 10
EC_FEATURE_BKLIGHT_SWITCH                   = 11
EC_FEATURE_WIFI_SWITCH                      = 12
EC_FEATURE_HOST_EVENTS                      = 13
EC_FEATURE_GPIO                             = 14
EC_FEATURE_I2C                              = 15
EC_FEATURE_CHARGER                          = 16
EC_FEATURE_BATTERY                          = 17
EC_FEATURE_SMART_BATTERY                    = 18
EC_FEATURE_HANG_DETECT                      = 19
EC_FEATURE_PMU                              = 20
EC_FEATURE_SUB_MCU                          = 21
EC_FEATURE_USB_PD                           = 22
EC_FEATURE_USB_MUX                          = 23
EC_FEATURE_MOTION_SENSE_FIFO                = 24
EC_FEATURE_VSTORE                           = 25
EC_FEATURE_USBC_SS_MUX_VIRTUAL              = 26
EC_FEATURE_RTC                              = 27
EC_FEATURE_FINGERPRINT                      = 28
EC_FEATURE_TOUCHPAD                         = 29
EC_FEATURE_RWSIG                            = 30
EC_FEATURE_DEVICE_EVENT                     = 31
EC_FEATURE_UNIFIED_WAKE_MASKS               = 32
EC_FEATURE_HOST_EVENT64                     = 33
EC_FEATURE_EXEC_IN_RAM                      = 34
EC_FEATURE_CEC                              = 35
EC_FEATURE_MOTION_SENSE_TIGHT_TIMESTAMPS    = 36
EC_FEATURE_REFINED_TABLET_MODE_HYSTERESIS   = 37
EC_FEATURE_SCP                              = 39
EC_FEATURE_ISH                              = 40

class cros_ec_command(Structure):
    _fields_ = [
        ('version', c_uint),
        ('command', c_uint),
        ('outsize', c_uint),
        ('insize', c_uint),
        ('result', c_uint),
        ('data', c_ubyte * EC_HOST_PARAM_SIZE)
    ]

class ec_params_hello(Structure):
    _fields_ = [
        ('in_data', c_uint)
    ]

class ec_response_hello(Structure):
    _fields_ = [
        ('out_data', c_uint)
    ]

class ec_params_get_features(Structure):
    _fields_ = [
        ('in_data', c_ulong)
    ]

class ec_response_get_features(Structure):
    _fields_ = [
        ('out_data', c_ulong)
    ]

def EC_FEATURE_MASK_0(event_code):
    return (1 << (event_code % 32))

def EC_FEATURE_MASK_1(event_code):
    return (1 << (event_code - 32))

def is_feature_supported(feature):
    global ECFEATURES

    if ECFEATURES == -1:
        fd = open("/dev/cros_ec", 'r')

        param = ec_params_get_features()
        response = ec_response_get_features()

        cmd = cros_ec_command()
        cmd.version = 0
        cmd.command = EC_CMD_GET_FEATURES
        cmd.insize = sizeof(param)
        cmd.outsize = sizeof(response)

        memmove(addressof(cmd.data), addressof(param), cmd.outsize)
        fcntl.ioctl(fd, EC_DEV_IOCXCMD, cmd)
        memmove(addressof(response), addressof(cmd.data), cmd.outsize)

        fd.close()

        if cmd.result == 0:
            ECFEATURES = response.out_data
        else:
            return False

    return (ECFEATURES & EC_FEATURE_MASK_0(feature)) > 0

def check_mcu_abi(s, name):
        if not os.path.exists("/dev/cros_" + name):
            s.skipTest("MCU " + name + " not supported, skipping")
        files = ["flashinfo", "reboot", "version"]
        sysfs_check_attributes_exists(s, "/sys/class/chromeos/", "cros_" + name, files, False)

