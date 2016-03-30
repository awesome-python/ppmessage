# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 .
# Guijin Ding, dingguijin@gmail.com
# All rights reserved
#
# backend/gcmpush.py 
# The entry form gcmpush service
#

from ppmessage.bootstrap.data import BOOTSTRAP_DATA
from ppmessage.core.constant import REDIS_GCMPUSH_KEY

import tornado.ioloop
import tornado.options
import tornado.httpserver

import sys
import logging
import datetime

class PushHandler():
    def __init__(self, _app):
        self.application = _app
        return
    
    def _one(self, _token, _msg):
        if self.gcm == None:
            logging.error("no gcm")
            return
        self.gcm.plaintext_request(registration_id=_token, collapse_key='ppmessage', data=_msg)
        return
    
    def _push(self, _app_uuid, _body, _config):
        _type = _body.get("mt")
        _subtype = _body.get("ms")
        _count = _config.get("unacked_notification_count")
        _title = push_title(_type, _subtype, _body.get("bo"), _config.get("user_language"))
        _token = _config.get("mqtt_android_token")
        _sound = None
        if not _config.get("user_silence_notification"):
            _sound = "beep.wav"
        _msg = {"title": _title, "sound": _sound, "count": _count}
        self._one(_token, _msg)
        return

    def task(self, _data):
        _config = _data.get("config")
        _body = _data.get("body")
        _app_uuid = _data.get("app_uuid")
        if _config == None or \
           _body == None or \
           _app_uuid == None:
            logging.error("Illegal request: %s." % str(_data))
            return
        self._push(_app_uuid, _body, _config)
        return

class GcmPushApp():
    def __init__(self, *args, **kwargs):
        _config = BOOTSTRAP_DATA.get("gcm")
        _api_key = _config.get("api_key")
        self.gcm = GCM(_api_key)
        return
        
    def outdate(self):
        _delta = datetime.timedelta(seconds=30)
        if self.gcm == None:
            return
        self.gcm.outdate(_delta)
        return

    def push(self):
        if self.gcm == None:
            logging.error("no gcm inited.")

        return

if __name__ == "__main__":
    tornado.options.parse_command_line()

    _config = BOOTSTRAP_DATA.get("gcm")
    _api_key = _config.get("api_key")
    if _api_key == None or len(_api_key) == 0:
        logging.info("No gcm api_key config, gcmpush can not start.")
        sys.exit()
    
    _app = GcmPushApp()
    logging.info("Starting gcmpush service......")
    # set the periodic check outdated connection
    tornado.ioloop.PeriodicCallback(_app.outdate, 1000*30).start()
    tornado.ioloop.PeriodicCallback(_app.push, 1000).start()
    tornado.ioloop.IOLoop.instance().start()
    
