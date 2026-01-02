
import WoDAssistant

import traceback
import os
import json

def init_data():
    data = {}
    try:
        os.makedirs(WoDAssistant.data.dataPath, exist_ok = True)
        with open(f'{WoDAssistant.data.dataPath}/config.json', 'r', encoding = 'utf-8') as f:
            data = json.loads(f.read())
        if 'listAdmin' in data:
            WoDAssistant.data.listAdmin = data['listAdmin']
        if 'listBroadcastGroup' in data:
            WoDAssistant.data.listBroadcastGroup = data['listBroadcastGroup']
        if 'listPartyID' in data:
            WoDAssistant.data.listPartyID = data['listPartyID']
    except Exception as e:
        traceback.print_exc()
        WoDAssistant.logger.logProc(4, f'加载配置出错')

def save_data():
    try:
        os.makedirs(WoDAssistant.data.dataPath, exist_ok = True)
        with open(f'{WoDAssistant.data.dataPath}/config.json', 'w', encoding = 'utf-8') as f:
            f.write(json.dumps({
                'listAdmin': WoDAssistant.data.listAdmin,
                'listBroadcastGroup': WoDAssistant.data.listBroadcastGroup,
                'listPartyID': WoDAssistant.data.listPartyID
            }))
    except Exception as e:
        traceback.print_exc()
        WoDAssistant.logger.logProc(4, f'写入配置出错')

def readCache(partyID: int):
    res = None
    try:
        os.makedirs(WoDAssistant.data.dataPath, exist_ok = True)
        with open(f'{WoDAssistant.data.dataPath}/cache_{partyID}.json', 'r', encoding = 'utf-8') as f:
            res = json.loads(f.read())
    except Exception as e:
        traceback.print_exc()
        WoDAssistant.logger.logProc(4, '读取缓存数据出现问题')
    return res

def writeCache(data: dict, partyID: int):
    try:
        os.makedirs(WoDAssistant.data.dataPath, exist_ok = True)
        with open(f'{WoDAssistant.data.dataPath}/cache_{partyID}.json', 'w', encoding = 'utf-8') as f:
            f.write(json.dumps(data, indent = 4, ensure_ascii = False))
    except Exception as e:
        traceback.print_exc()
        WoDAssistant.logger.logProc(4, '写入缓存数据出现问题')
