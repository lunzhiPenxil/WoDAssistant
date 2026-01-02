# -*- encoding: utf-8 -*-

import OlivOS
import WoDAssistant

import traceback
import requests
import json

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
        WoDAssistant.logger.logProc(4, '数据解析失败')
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
        WoDAssistant.logger.logProc(3, '名称解析失败')
    return res

def get_fetchDropAnalysis(partyID: int):
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
        WoDAssistant.logger.logProc(4, '数据解析失败')
        responseData = None
        res = None
    if responseData is not None:
        res = responseData
    return res

def diff_fetchDropAnalysis(data: dict, partyID: int):
    res = []
    old_data = WoDAssistant.dataIO.readCache(partyID)
    WoDAssistant.dataIO.writeCache(data, partyID)
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
            WoDAssistant.logger.logProc(4, '比较数据时出现问题')
            res = []
    elif 'code' in data \
    and 200 != data['code']:
        WoDAssistant.logger.logProc(4, f"接口连接失败 {data['code']}: {data['msg']}")
    return res
