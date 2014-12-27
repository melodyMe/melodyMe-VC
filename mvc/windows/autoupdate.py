"""Autoupdate functionality """

import ctypes
import _winreg as winreg
import logging

winsparkle = ctypes.cdll.WinSparkle

APPCAST_URL = 'http://updates.plexilabs.me/en/melodyMe/video-converter/update.xml'

def startup():
    enable_automatic_checks()
    winsparkle.win_sparkle_set_appcast_url(APPCAST_URL)
    winsparkle.win_sparkle_init()

def shutdown():
    winsparkle.win_sparkle_cleanup()

def enable_automatic_checks():
    # We should be able to use win_sparkle_set_automatic_check_for_updates,
    # but that's only available after version 0.4 and the current release
    # version is 0.4
    with open_winsparkle_key() as winsparkle_key:
	if not check_for_updates_set(winsparkle_key):
	    set_default_check_for_updates(winsparkle_key)

def open_winsparkle_key():
    """Open the MVC WinSparkle registry key
    
    If any components are not created yet, we will try to create them
    """
    with open_or_create_key(winreg.HKEY_CURRENT_USER, "Software") as software:
	with open_or_create_key(software,
		"PlexiLabs") as pcf:
	    with open_or_create_key(pcf, "melodyMe Video Converter") as mvc:
		return open_or_create_key(mvc, "WinSparkle",
			write_access=True)

def open_or_create_key(key, subkey, write_access=False):
    if write_access:
	sam = winreg.KEY_READ | winreg.KEY_WRITE
    else:
	sam = winreg.KEY_READ
    try:
	return winreg.OpenKey(key, subkey, 0, sam)
    except OSError, e:
	if e.errno == 2:
	    # Not Found error.  We should create the key
	    return winreg.CreateKey(key, subkey)
	else:
	    raise

def check_for_updates_set(winsparkle_key):
    try:
	winreg.QueryValueEx(winsparkle_key, "CheckForUpdates")
    except OSError, e:
	if e.errno == 2:
	    # not found error.
	    return False
	else:
	    raise
    else:
	return True


def set_default_check_for_updates(winsparkle_key):
    """Initialize the WinSparkle regstry values with our defaults.

    :param mvc_key winreg.HKey object for to the MVC registry
    """
    logging.info("Writing WinSparkle keys")
    winreg.SetValueEx(winsparkle_key, "CheckForUpdates", 0, winreg.REG_SZ, "1")
