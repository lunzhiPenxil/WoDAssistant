# -*- encoding: utf-8 -*-

import OlivOS

import platform

pluginName = 'WoD小助手'

version = '0.6.1'
svn = 61

OlivOSInfo = f"[Python {platform.python_version()} OlivOS {OlivOS.infoAPI.OlivOS_Version}]"

dataPath = './plugin/data/WoDAssistant'

gProc: 'OlivOS.pluginAPI.shallow|None' = None

listAdmin = []
listBroadcastGroup = {}
listPartyID = []

broadcastTimer = 300
