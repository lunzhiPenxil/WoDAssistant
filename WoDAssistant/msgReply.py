# -*- encoding: utf-8 -*-

import OlivOS
import WoDAssistant

import threading
import time

import requests
import json
import traceback
import os

listBroadcastGroup = WoDAssistant.broadcastData.listBroadcastGroup

listPartyID = WoDAssistant.broadcastData.listPartyID

def unity_reply(plugin_event, Proc):
    pass

def unity_init_after(plugin_event, Proc):
    WoDAssistant.main.gProc = Proc
    threading.Thread(target = threadingSend).start()

def sendMessageForce(botHash, send_type, target_id, message):
    Proc = WoDAssistant.main.gProc
    if Proc is not None \
    and botHash in Proc.Proc_data['bot_info_dict']:
        pluginName = WoDAssistant.main.pluginName
        plugin_event = OlivOS.API.Event(
            OlivOS.contentAPI.fake_sdk_event(
                bot_info = Proc.Proc_data['bot_info_dict'][botHash],
                fakename = pluginName
            ),
            Proc.log
        )
        plugin_event.send(send_type, target_id, message)

def threadingSend():
    while True:
        for partyID in listPartyID:
            try:
                logProc(2, f"开始更新团队[ID:{partyID}]的数据")
                messageList = release_reply(
                    get_groupName(get_fetchList(partyID), partyID),
                    diff_fetchDropAnalysis(
                        get_fetchDropAnalysis(partyID),
                        partyID
                    )
                )
                logProc(2, f'已经完成团队[ID:{partyID}]数据更新')
                for message in messageList:
                    time.sleep(1)
                    broadcastSend(message, partyID)
            except Exception as e:
                traceback.print_exc()
                logProc(4, f'团队[ID:{partyID}]数据更新出现问题')
        time.sleep(300)

def broadcastSend(message: str, partyID: int):
    for botHashThis in listBroadcastGroup:
        if str(partyID) in listBroadcastGroup[botHashThis]:
            for groupIDThis in listBroadcastGroup[botHashThis][str(partyID)]:
                sendMessageForce(
                    botHash = botHashThis,
                    send_type = 'group',
                    target_id = groupIDThis,
                    message = message
                )

def get_fetchList(partyID: int):
    res = None
    responseData = None
    try:
        response = requests.request(
            method = 'POST',
            url = 'https://www.christophero.xyz/wod/group/fetchList',
            headers = {
                'User-Agent': f'OlivOS/{OlivOS.infoAPI.OlivOS_Header_UA} WoDAssistant',
                'Content-Type': 'application/json'
            },
            data = json.dumps(obj = {
                "page": {
                    "current": 1,
                    "size": 1
                },
                "query": {
                    "id": partyID,
                    "name": ""
                }
            }),
            timeout = 60
        )
        responseData = json.loads(response.text)
    except Exception as e:
        traceback.print_exc()
        logProc(4, '数据解析失败')
        responseData = None
        res = None
    if responseData is not None:
        res = responseData
    return res

def get_groupName(data: dict, partyID: int):
    res = f"团队[{partyID}]"
    try:
        if data is not None \
        and 'code' in data \
        and 200 == data['code'] \
        and 'status' in data \
        and 1 == data['status'] \
        and 'data' in data \
        and type(data['data']) is dict \
        and 'list' in data['data'] \
        and type(data['data']['list']) is list \
        and len(data['data']['list']) > 0:
            res = data['data']['list'][0]['name']
    except Exception as e:
        traceback.print_exc()
        logProc(3, '名称解析失败')
    return res
        

def get_fetchDropAnalysis(partyID):
    res = None
    responseData = None
    try:
        response = requests.request(
            method = 'POST',
            url = 'https://www.christophero.xyz/wod/item/fetchDropAnalysis',
            headers = {
                'User-Agent': f'OlivOS/{OlivOS.infoAPI.OlivOS_Header_UA} WoDAssistant',
                'Content-Type': 'application/json'
            },
            data = json.dumps(obj = {
                'groupId': partyID,
            }),
            timeout = 60
        )
        responseData = json.loads(response.text)
    except Exception as e:
        traceback.print_exc()
        logProc(4, '数据解析失败')
        responseData = None
        res = None
    if responseData is not None:
        res = responseData
    return res

def diff_fetchDropAnalysis(data, partyID: int):
    res = []
    old_data = readData(partyID)
    writeData(data, partyID)
    if old_data is not None \
    and 'code' in old_data \
    and 200 == old_data['code'] \
    and 'status' in old_data \
    and 1 == old_data['status'] \
    and 'data' in old_data \
    and type(old_data['data']) is list \
    and 'code' in data \
    and 200 == data['code'] \
    and 'status' in data \
    and 1 == data['status'] \
    and 'data' in data \
    and type(data['data']) is list:
        try:
            for dataThis in data['data']:
                flagHit = False
                flagChange = False
                dataThisObj = {
                    'new': dataThis,
                    'old': None
                }
                for old_dataThis in old_data['data']:
                    if dataThis['id'] == old_dataThis['id']:
                        flagHit = True
                        if dataThis['lastDungeonTime'] != old_dataThis['lastDungeonTime']:
                            flagChange = True
                            dataThisObj['old'] = old_dataThis
                        break
                if not flagHit:
                    flagChange = True
                    dataThisObj['old'] = None
                if flagChange:
                    res.append(dataThisObj)
        except Exception as e:
            traceback.print_exc()
            logProc(4, '比较数据时出现问题')
            res = []
    elif 'code' in data \
    and 200 != data['code']:
        logProc(4, f"接口连接失败 {data['code']}: {data['msg']}")
    return res

def writeData(data, partyID: int):
    try:
        os.makedirs('./plugin/data/WoDAssistant', exist_ok = True)
        with open(f'./plugin/data/WoDAssistant/cache_{partyID}.json', 'w', encoding = 'utf-8') as f:
            f.write(json.dumps(data, indent = 4, ensure_ascii = False))
    except Exception as e:
        traceback.print_exc()
        logProc(4, '写入缓存数据出现问题')

def readData(partyID: int):
    res = None
    try:
        os.makedirs('./plugin/data/WoDAssistant', exist_ok = True)
        with open(f'./plugin/data/WoDAssistant/cache_{partyID}.json', 'r', encoding = 'utf-8') as f:
            res = json.loads(f.read())
    except Exception as e:
        traceback.print_exc()
        logProc(4, '读取缓存数据出现问题')
    return res

def release_reply(groupName:str, dataList: list):
    res = []
    for dataListThisObj in dataList:
        dataListThis = dataListThisObj['new']
        old_dataListThis = dataListThisObj['old']
        lastDungeonTime = dataListThis['lastDungeonTime']
        intervalTime = '' if dataListThis['intervalTime'] is None else f"[{dataListThis['intervalTime']}]"
        name = dataListThis['name']
        times = dataListThis['times']
        level = f"Lv. {dataListThis['minLv']} ~ {dataListThis['maxLv']}"
        lvDiff = dataListThis['lvDiff']
        dropListData = []
        for dataListThis_this in dataListThis['dropList']:
            diff_str = ''
            newDrop_str = ''
            uniqType_str = ''
            if dataListThis_this['newDrop'] is True:
                diff_count = 0
                if old_dataListThis is not None:
                    for old_dataListThis_this in old_dataListThis['dropList']:
                        if old_dataListThis_this['id'] == dataListThis_this['id']:
                            diff_count = dataListThis_this['total'] - old_dataListThis_this['total']
                            newDrop_str = '★'
                            if diff_count > 0:
                                diff_str = f" (+{diff_count})"
                            break
            if dataListThis_this['uniq'] != 'N':
                uniqType_str = f"[{dataListThis_this['uniq']}]"
            dropListData.append(f"{newDrop_str}{dataListThis_this['name']}{uniqType_str}: {dataListThis_this['total']}{diff_str}{(' / ' + str(dataListThis_this['maxDrop'])) if dataListThis_this['maxDrop'] != 0 else ''}")
        dropTotalList = '\n'.join(dropListData)
        resThis = f" {'='*2} 「{groupName}」 {'='*2}\n{intervalTime}{name} - 第{times}次\n{level} 难度{lvDiff}\n{lastDungeonTime}\n {'='*4} 【全部产出】 {'='*4}\n{dropTotalList}"
        res.append(resThis)
    return res

def logProc(level, message, segment = []):
    Proc = WoDAssistant.main.gProc
    if Proc is not None:
        try:
            Proc.log(
                log_level = level,
                log_message = message,
                log_segment = [(WoDAssistant.main.pluginName, 'default')] + segment
            )
        except Exception as e:
            traceback.print_exc()
