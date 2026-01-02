# -*- encoding: utf-8 -*-

import WoDAssistant

import traceback

def logProc(level: int, message: str, segment: list = []):
    Proc = WoDAssistant.data.gProc
    if Proc is not None:
        try:
            Proc.log(
                log_level = level,
                log_message = message,
                log_segment = [(WoDAssistant.data.pluginName, 'default')] + segment
            )
        except Exception as e:
            traceback.print_exc()
