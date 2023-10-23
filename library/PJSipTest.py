#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#https://github.com/MartyTremblay/sip2mqtt/blob/master/sip2mqtt.py
#https://github.com/alyssaong1/VoIPBot/blob/master/src/runclient.py
#https://github.com/cristeab/autodialer/blob/master/core/softphone.py
#https://github.com/crs4/most-voip/blob/master/python/src/most/voip/api_backend.py
#https://github.com/pjsip/pjproject/issues/3125
#https://gist.github.com/hu55a1n1/6d00be6316013fdde5e5ed20549ebbef


__app__ = "PJSip"
__VERSION__ = "0.2"
__DATE__ = "31.07.2023"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2023 Markus Schiesser"
__license__ = 'GPL v3'

import copy

import pjsua2 as pj
import threading
from multiprocessing import Process, Queue, Pipe
import logging
import json
import paho.mqtt.client as mqtt


import time


# mod2 creates its own logger, as a sub logger to 'spam'
logger = logging.getLogger('pjsua.mod2')

notification = False
callState = False
logHandle = False
outerClassObject = False

class Logger(pj.LogWriter):
    """
    Logger to receive log messages from pjsua2
    """
    def __init__(self):
        pj.LogWriter.__init__(self)

    def write(self, entry):
        """entry fields:
            int		level;
            string	msg;
            long	threadId;
            string	threadName;
        """


        if entry.level == 5:
            tags = ('trace',)
            logger.debug(entry.msg)
        elif entry.level == 3:
            logger.info(entry.msg)
        elif entry.level == 2:
            logger.warning(entry.msg)
        elif entry.level <= 1:
            logger.error(entry.msg)
        else:
            logger.info(entry.msg)
        #writeLog(entry)
       # print('2222',tags, entry.msg + "\r\n")

class MyLogWriter(pj.LogWriter):
    def write(self, entry):
        print("This is Python:", entry.msg)

class PJSip(object):

  #  callState = None
    def __init__(self,logger,pipe):
  #  def __init__(self,callback,root_logger):
      #  self._calbackk = callbackz

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)

        global logHandle
        logHandle = self._log
        global outerClassObject
        outerClassObject = self
        self.logger = Logger()

        self._log.debug('Create PJSip mqttclient Object')
        self._ep = None
        self._acc = None

        self._host = None
        self._port = 5060

        self._debugLevel = 4

        self._call = None

        self._pipe = pipe
       # self._notification = None

        #self.accountState = None
        #self._callState = None

    def log(self,msg):
        self._log.debug(msg)


    class MyLogWriter(pj.LogWriter):
        def write(self, entry):
            print("Logger:", entry.msg)



    class MyAccount(pj.Account):
        def __init__(self):
            pj.Account.__init__(self)
           # pj.Account.__init__(self, account)
            global notification

        def onRegState(self, prm):
           # global notification
            print("***OnRegState: ", prm.reason)
       #     self._log.info("***OnRegState: %s" % prm.reason)
            notification(prm.reason)
        #    self._notification('**OnState' + str(prm.reason))
         #   self.accountState = prm.reason

        def onIncomingCall(self, prm):
            c = self.Call(self, call_id=prm.callId)
            call_prm = pj.CallOpParam()

            call_prm.statusCode = 180
            c.answer(call_prm)
            ci = c.getInfo()
            # Unless this callback is implemented, the default behavior is to reject the call with default status code.
            self._log.info("SIP: Incoming call from " + ci.remoteUri())
           # broker.publish(args.mqtt_topic, payload="{\"verb\": \"incoming\", \"caller\":\"" + extract_caller_id(
            #    call.info().remote_uri) + "\", \"uri\":" + json.dumps(call.info().remote_uri) + "}", qos=0, retain=True)

          #  current_call = call
         #   print(call.info())
            #call_cb = SMCallCallback(current_call)
            #current_call.set_callback(call_cb)



    class MyCall(pj.Call):

        def __init__(self, acc, peer_uri='', chat=None, call_id=pj.PJSUA_INVALID_ID):
            pj.Call.__init__(self, acc, call_id)
            self.acc = acc
            self.wav_player = None
            self.wav_recorder = None
            print('Create MyCall object')

            global notification

        def __enter__(self):
            print('Create MyCall obejct')

        def __exit__(self, exc_type, exc_val, exc_tb):
            print('Closing MyCall', exc_type,exc_val,exc_tb)

        def __del__(self):
            print("DELETE Call Object")


        def onCallStateNew(self, prm):
            ci = self.getInfo()
            self.connected = ci.state == pj.PJSIP_INV_STATE_CONFIRMED
            self.recorder = None
            if (self.connected == True):
                player = pj.AudioMediaPlayer()
                # Play welcome message
                player.createPlayer("temp/announcement.wav");

                self.recorder = pj.AudioMediaRecorder()
                self.recorder.createRecorder('temp/file.wav', enc_type=0, max_size=0,
                                             options=0);
                i = 0
                for media in ci.media:

                    if (media.type == pj.PJMEDIA_TYPE_AUDIO):
                        self.aud_med = self.getMedia(i);
                        break;
                    i = i + 1;
                if self.aud_med != None:
                    # This will connect the sound device/mic to the call audio media
                    mym = pj.AudioMedia.typecastFromMedia(self.aud_med)
                    player.startTransmit(mym);
                    # mym.startTransmit( self.recorder);
            if (ci.state == pj.PJSIP_INV_STATE_DISCONNECTED):
                print(">>>>>>>>>>>>>>>>>>>>>>> Call disconnected")
                # mym= pj.AudioMedia.typecastFromMedia(self.aud_med)
                # mym.stopTransmit(self.recorder);
            raise Exception('onCallState done!')

            # override the function at original parent class
        # parent class's function can be called by super().onCallState()
        def onCallState(self, prm):
            global callState
            print('onCallState')

            ci = self.getInfo()
            print("*** Call: {} [{}]".format(ci.remoteUri, ci.lastStatusCode))
            if ci.lastStatusCode == 404:
                print("call can't established with code 404!")
                # quitPJSUA()
            if ci.state == pj.PJSIP_INV_STATE_CALLING:
                print('***CALLIJG***', ci.lastStatusCode)
                notification({
                    "INFO":"CALLING",
                    "STATUS Code": ci.lastStatusCode
                })

            if ci.state == pj.PJSIP_INV_STATE_CONNECTING:
                print('***CONNECTING***', ci.lastStatusCode)
                notification({
                    "INFO":"CONNECTING",
                    "STATUS Code": ci.lastStatusCode
                })

            if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
                print('***CONFIRMED***', ci.lastStatusCode)
                notification({
                    "INFO":"CONFIREMDE",
                    "STATUS Code": ci.lastStatusCode
                })

                print(ci.media, ci.media[0], ci.media.size)
                if ci.media[0].type == pj.PJMEDIA_TYPE_AUDIO:
                    print('***AUDIO***')
                    notification({
                        "INFO": "AUDIO CAll",
                        "STATUS Code": ci.lastStatusCode
                    })
                if ci.media[0].status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    print('***MEDIA ACTIVE***')
                    notification({
                        "INFO": "AUDIO ACTIVE",
                        "STATUS Code": ci.lastStatusCode
                    })
                    aud_med = None

                    try:
                        # get the "local" media
                        aud_med = self.getAudioMedia(-1)
                        print('Aud_med', aud_med)

                    except pj.Error as e:
                        print("exception!!: {}".format(e.args))

                    if not self.wav_player:
                        #self.wav_player = pj.AudioMediaPlayer()
                        self.wav_player = pj.AudioMediaPlayer()
                        try:
                            self.wav_player.createPlayer("temp/announcement.wav",pj.PJMEDIA_FILE_NO_LOOP)
                            aud_med = self.getAudioMedia(-1)
                            print('player created', aud_med)
                        #   self.wav_player.startTransmit(aud_med)
                        except pj.Error as e:
                            print("Exception!!: failed opening wav file")
                            del self.wav_player
                            self.wav_player = None
                        else:
                            print('Start playbacksss')
                        #   self.wav_player.startTransmit(aud_med)
                    if self.wav_player:
                        #print('play message')
                        notification({
                            "INFO": "PLAY MESSAGE",
                            "STATUS Code": ci.lastStatusCode
                        })
                        self.wav_player.startTransmit(aud_med)
                        notification({
                            "INFO": "PLAY MESSAGE COMPLETED",
                            "STATUS Code": ci.lastStatusCode
                        })
                        #print('Message played completed')

            if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
                print('***DISCONNECTING***', ci.lastStatusCode)
                notification({
                    "INFO": "DISCONNECTING",
                    "STATUS Code": ci.lastStatusCode
                })
                callState = 'CLOSE'

        def onDtmfDigit(self, prm):
            print('Received DTMF', prm.digit)
            notification({
                "INFO": "DTMF RECEIVED",
                "DTMF": prm.digit
            })

        def onCallMediaStateOld(self, prm):
            ci = self.getInfo()
            print('TEST',ci,prm)

            for mi in ci.media:
                print('TEST2',ci.media.size(), mi)
                if mi.type == pj.PJMEDIA_TYPE_AUDIO:
                    print('pj.PJMEDIA_TYPE_AUDIO')
                if mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    print('ACTIVE')



            aud_med = None

            try:
                # get the "local" media
                aud_med = self.getAudioMedia(-1)
                print('Aud_med',aud_med)
            except pj.Error as e:
                print("exception!!: {}".format(e.args))


            if not self.wav_player:
                self.wav_player = pj.AudioMediaPlayer()
                try:
                    self.wav_player.createPlayer("./input.16.wav")
                    aud_med = self.getAudioMedia(-1)
                    print('player created',aud_med)
                 #   self.wav_player.startTransmit(aud_med)
                except pj.Error as e:
                    print("Exception!!: failed opening wav file")
                    del self.wav_player
                    self.wav_player = None
                else:
                    print('Start playbacksss')
                 #   self.wav_player.startTransmit(aud_med)
            if self.wav_player:
                print('play message')
                self.wav_player.startTransmit(aud_med)

    class MyMediaPlayer(pj.AudioMediaPlayer):
        def __init__(self):
            print('INIT-------------------------------------------')
            super().__init__()

        def onEof2(self):
            print('playback completed')
            notification({
                "INFO": "Message Played"
            })

        def play_file(self, audio_media: pj.AudioMedia, sound_file_name: str) -> None:
            print('play_file')
            notification({
                "INFO": "Play Message"
            })

    def callNumber(self,id:str) -> bool:
        global callState

        uri = 'sip:' + id +'@' + self._host + ':' + str(self._port)

       # calls=['sip:0795678728@192.168.2.1:5060']
        print('Call URI ', uri, self._call)

        self._call = self.MyCall(self._acc)

        self._prm = pj.CallOpParam(True)
        self._prm.opt.audioCount = 1
        self._prm.opt.videoCount = 0

        print('make call', callState, self._prm)
        self._call.makeCall(uri, self._prm)
      #  print(callState != 'CLOSE')
        while callState != 'CLOSE':
            self._ep.libHandleEvents(100)
           # print('CallState:',callState)
      #  while True:
       #     self._ep.libHandleEvents(10)
        # while True:
        #    if end > time.time():
        #       pj.Endpoint.instance().libHandleEvents(20)
        callState = False
        print('-done--')
       # self._ep.hangupAllCalls()
        self.hangup()
        del self._call
        self._call = None


    def hangup(self):
        self._ep.hangupAllCalls()

    def call(self,id):
        print('call',id)
        _id = copy.deepcopy(id)
        self.callNumber(_id)

    def setNotification(self,sink: str) -> bool:
        self._log.debug('setNotification %s'% sink)
        global notification
        notification = sink
        notification('TEST')
        return True

    def logNotification(self,msg: str) -> bool:
        self._log.debug('PJSipLog: %s'%msg)
        return True

    def setDebugLevel(self,level: int)->bool:
        self_debugLevel = level
        return True




    def setupAccount(self,host: str,user: str ,passwd: str) -> bool:

        self._host = host

        # init the lib
        self._ep = pj.Endpoint()
        self._ep.libCreate()


       # lib.init(log_cfg=pj.LogConfig(level=3, callback=log_cb))
        #https://stackoverflow.com/questions/62095804/calling-pj-thread-register-from-python
        self._ep_cfg = pj.EpConfig()
        # Python does not like PJSUA2's thread. It will result in segment fault
        self._ep_cfg.uaConfig.threadCnt = 0
        self._ep_cfg.uaConfig.mainThreadOnly = True
        #self._ep.libRegisterThread("PJSUA-THREAD")
       # print('***REGISTER***',self._ep.libIsThreadRegistered())

        #Debug
        #https://github.com/zlargon/pjsip/blob/master/pjsip-apps/src/swig/python/test.py
      #  self._ep_cfg.logConfig.level = self._debugLevel
       # self._ep_cfg.logConfig.consoleLevel = 5

        lw = self.MyLogWriter()
        self._ep_cfg.logConfig.writer = lw
        self._ep_cfg.logConfig.decor = self._ep_cfg.logConfig.decor & ~(pj.PJ_LOG_HAS_CR | pj.PJ_LOG_HAS_NEWLINE)
        #self._ep_cfg.logConfig.writer = self.logger

       # self._ep_cfg.logConfig.decor = self._ep_cfg.logConfig.decor & ~(pj.PJ_LOG_HAS_CR | pj.PJ_LOG_HAS_NEWLINE)
        #log_cfg = pj.LogConfig(level=3, callback=log_cb)
       # w = MyLogWriter()
       # ep_cfg.logConfig.writer = l._log

        # using thread in python may cause some problem
       # self._ep_cfg.uaConfig.threadCnt = 1
       # self._ep_cfg.uaConfig.mainThreadOnly = True

        self._ep.libInit(self._ep_cfg)

        # add some config
        tcfg = pj.TransportConfig()
        # tcfg.port = 5060
        self._ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tcfg)

        # add account config
        self._acc_cfg = pj.AccountConfig()
        self._acc_cfg.idUri = 'sip:{}@{}'.format(user,host)

        print("*** start sending SIP REGISTER ***")
        self._acc_cfg.regConfig.registrarUri = 'sip:' + host

        # if there needed credential to login, just add following lines
        cred = pj.AuthCredInfo("digest", "*", user, 0, passwd)
        self._acc_cfg.sipConfig.authCreds.append(cred)

        self._acc = self.MyAccount()
        self._acc.create(self._acc_cfg)
        # acc = pj.Account()
        # acc.create(acc_cfg)

        result = self._ep.libStart()
        print("*** PJSUA2 STARTED ***", result)
      #  self._notification('STARTED')

        # use null device as conference bridge, instead of local sound card
        pj.Endpoint.instance().audDevManager().setNullDev()
        print('*** Complete ***')
        while True:
            print('?')
            self._ep.libHandleEvents(10)
            print('!')
           # pj.Endpoint.instance().libHandleEvents(20)
            #x = self._pipe.recv()
            x = self._pipe.get()
            print('X',x)
            self.callNumber(x)

        return result

    def shutdown(self):
        self._ep.libDestroy()

def callback(notification):
    print('CALLBACK:',notification)

class mqttclient(object):

    def __init__(self,pipe):
        self._pipe = pipe
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.on_subscribe = self.on_subscribe

    def connect(self,host):
        self._client.connect(host,1883,60)
        self._client.loop_start()

        print('STart MQTT')

    def startMQTT(self):
       # self._client.loop_forever()
        self._client.loop_start()

    def subscribe(self,topic:str,callback:str=None):
        self._client.message_callback_add(topic,callback)
        print('Subscribe mqtt topic',callback)
        (_result, _mid) = self._client.subscribe(topic)

    def subscribeNoCallback(self,topic):
        (_result, _mid) = self._client.subscribe(topic)

    def publish(self,topic,payload):
        self._client.publish(topic, json.dumps(payload), qos=0, retain=False)
        print('Publiseh',payload)

    def on_connect(self,client, userdata, flags, rc):
        print("MQTT Connection returned result: ", rc)

    def on_message(self,client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        #self._pipe.send(str(msg.payload))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print('on subscribe')




class caller(object):
    def __init__(self):
        self._voip = None
        self._mqtt = None

        self._queue = Queue()
        self._mqttPipe, self._pjsuaPipe = Pipe()

    def start_pjsua(self,pipe):

        self._voip = PJSip('PJSip',pipe)
        self._voip.setNotification(self.callback)
        self._voip.setupAccount('192.168.2.1','220','Swisscom10%')
       # self._queue.put(dumps(self._voip))
       # while not self._queue.empty():
        #    print('QUE',self._queue.get())
        print('VOIP OBJ',self._voip)

    def start_mqtt(self,pipe):
        self._mqtt = mqttclient(pipe)
        self._mqtt.connect('192.168.2.20')
        self._mqtt.subscribe('/TEST',self.brokercallback)
      #  self._mqtt.subscribeNoCallback('/TEST')
      #  self._mqtt.startMQTT()
        while True:
            time.sleep(10)
            self._mqtt.publish('/TEST/MGS', 'TEST')

    def setup(self):
       # q = Queue()
      #  mqttPipe, pjsuaPipe = Pipe()

        pjsua = Process(target=self.start_pjsua, args=(self._queue,))
       # pjsua = Process(target=self.start_pjsua,args=(self._pjsuaPipe,))
        print(pjsua)
        pjsua.start()

        mqtt = Process(target=self.start_mqtt,args=(self._queue,))
     #   mqtt = Process(target=self.start_mqtt, args=(self._mqttPipe,))
        print(mqtt)
        mqtt.start()

        pjsua.join()
        mqtt.join()

    def dail(self,_id):
        id = self._queue.get()
        print(id,self._voip)
       # self._voip.callNumber(id)
        #time.sleep(5)
        pass

    def brokercallback(self,client,userdata,msg):
        print('MSG from broker',msg.payload)
        x = json.loads(msg.payload)
        y = x["ID"]
       # self._pjsuaPipe.send(y)
        self._queue.put(y)
      #  self.dail(y)
    def callback(self, notification):
        print('Callback:', notification)
        print('mqqtt', self._mqtt)
        if self._mqtt is not None:
            self._mqtt.publish('/TEST/MGS',notification)

    def shutdown(self):
        self._voip.shutdown()




if __name__ == '__main__':

    _caller = caller()
    _caller.setup()
   # _caller.dail('0795678728')
   # _caller.dail('0795678728')
    while True:
        time.sleep(10)

    _caller.shutdown()

  #  x = 0
  #  _voip = PJSip('PJSip')
  #  print('object',_voip)
  #  _voip.setNotification(callback)
  #  _voip.setupAccount('192.168.2.1','220','Swisscom10%')

   # _voip.callNumber('0795678728')
   # time.sleep(2)
   # _voip.callNumber('0795678728')
   # time.sleep(5)
   # _voip.callNumber('0795678728')
   # time.sleep(5)
   # _voip.callNumber('204')
   # _voip.StartCall()
   # time.sleep(10)
   # _voip.shutdown()

