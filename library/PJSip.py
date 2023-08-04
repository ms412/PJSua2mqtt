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


__app__ = "PJSip"
__VERSION__ = "0.2"
__DATE__ = "31.07.2023"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2023 Markus Schiesser"
__license__ = 'GPL v3'

import pjsua2 as pj
import logging
import time
import sys


def _setup_logger():
    global logger
    if not logger:
        logger = logging.getLogger("Voip")  # ('Voip')

        handler = logging.StreamHandler()
        #         rootFormatter = logging.Formatter('%(name)s - %(levelname)s: %(msg)s')
        #         handler.setFormatter(rootFormatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)



class PJSip:

    def __init__(self):
  #  def __init__(self,callback,root_logger):
      #  self._calbackk = callbackz
        self._ep = None
        self._acc = None

        self._host = None
        self._port = 5060

        self._notification = None

        self.accountState = None



    class MyAccount(pj.Account):
        def onRegState(self, prm):
            print("***OnRegState: ", prm.reason)
            self.accountState = prm.reason

    class Call(pj.Call):

        def __init__(self, acc, peer_uri='', chat=None, call_id=pj.PJSUA_INVALID_ID):
            pj.Call.__init__(self, acc, call_id)
            self.acc = acc
            self.wav_player = None
            self.wav_recorder = None

        # override the function at original parent class
        # parent class's function can be called by super().onCallState()
        def onCallState(self, prm):
            ci = self.getInfo()
            print("*** Call: {} [{}]".format(ci.remoteUri, ci.lastStatusCode))
            if ci.lastStatusCode == 404:
                print("call can't established with code 404!")
                # quitPJSUA()
            if ci.state == pj.PJSIP_INV_STATE_CALLING:
                print('***CALLIJG***', ci.lastStatusCode)
            if ci.state == pj.PJSIP_INV_STATE_CONNECTING:
                print('***CONNECTING***', ci.lastStatusCode)
            if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
                print('***CONFIRMED***', ci.lastStatusCode)
                print(ci.media, ci.media[0], ci.media.size)
                if ci.media[0].type == pj.PJMEDIA_TYPE_AUDIO:
                    print('***AUDIO***')
                if ci.media[0].status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    print('***MEDIA ACTIVE***')
            if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
                print('***DISCONNECTING***', ci.lastStatusCode)

        def onCallMediaState(self, prm):
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

        def onDtmfDigit(self, prm):
            print('Received DTMF', prm.digit)

    def callNumber(self,id:str) -> bool:

        uri = 'sip:' + id +'@' + self._host + ':' + str(self._port)

       # calls=['sip:0795678728@192.168.2.1:5060']
        call = self.Call(self._acc)
        self._prm = pj.CallOpParam(True)
        self._prm.opt.audioCount = 1
        self._prm.opt.videoCount = 0
        call.makeCall(uri, self._prm)
        while True:
            self._ep.libHandleEvents(10)
        # while True:
        #    if end > time.time():
        #       pj.Endpoint.instance().libHandleEvents(20)
        self._ep.hangupAllCalls()

    def setNotification(self,sink: str) -> bool:
        self._notification = sink
        return True

    def setupAccount(self,host: str,user: str ,passwd: str) -> bool:

        self._host = host

        # init the lib
        self._ep = pj.Endpoint()
        self._ep.libCreate()

        self._ep_cfg = pj.EpConfig()
        #Debug
        self._ep_cfg.logConfig.level = 6
        self._ep_cfg.logConfig.consoleLevel = 6

        # using thread in python may cause some problem
        self._ep_cfg.uaConfig.threadCnt = 0
        self._ep_cfg.uaConfig.mainThreadOnly = True
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

        # use null device as conference bridge, instead of local sound card
        pj.Endpoint.instance().audDevManager().setNullDev()
        print('*** Complete ***')

        return result

    def StartCall(self):
        ep = None

        # init the lib
        ep = pj.Endpoint()
        ep.libCreate()
        ep_cfg = pj.EpConfig()
        #Debug
        ep_cfg.logConfig.level = 1
        ep_cfg.logConfig.consoleLevel = 1

        # using thread in python may cause some problem
        ep_cfg.uaConfig.threadCnt = 0
        ep_cfg.uaConfig.mainThreadOnly = True
        ep.libInit(ep_cfg)

        # add some config
        tcfg = pj.TransportConfig()
        # tcfg.port = 5060
        ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tcfg)

        # add account config
        acc_cfg = pj.AccountConfig()
     #   acc_cfg.idUri = "sip:{}@{}".format(args.username,re.findall("sip:(.*)", args.registrarURI)[0])
        acc_cfg.idUri = 'sip:220@192.168.2.1'

        print("*** start sending SIP REGISTER ***")
        acc_cfg.regConfig.registrarUri = 'sip:192.168.2.1'

        # if there needed credential to login, just add following lines
        cred = pj.AuthCredInfo("digest", "*", '220', 0, 'Swisscom10%')
        acc_cfg.sipConfig.authCreds.append(cred)


        acc = self.MyAccount()
        acc.create(acc_cfg)
       # acc = pj.Account()
       # acc.create(acc_cfg)

        ep.libStart()
        print("*** PJSUA2 STARTED ***")

        # use null device as conference bridge, instead of local sound card
        pj.Endpoint.instance().audDevManager().setNullDev()

        calls=['sip:0795678728@192.168.2.1:5060']
        for item in calls:
            call = self.Call(acc)
            prm = pj.CallOpParam(True)
            prm.opt.audioCount = 1
            prm.opt.videoCount = 0
            call.makeCall(item, prm)

            # hangup all call after the time we specified at args(sec)
            #sleep4PJSUA2(args.callTime)
            start = time.time()
            end = start + 10
            print(time.time())
            while True:
                ep.libHandleEvents(10)
           # while True:
            #    if end > time.time():
             #       pj.Endpoint.instance().libHandleEvents(20)
            ep.hangupAllCalls()

            del call
        print("*** PJSUA2 SHUTTING DOWN ***")
        del acc

        print("\nPress ENTER to quit")
        sys.stdin.readline()


    # close the library
        try:
            ep.libDestroy()
        except pj.Error as e:
            print("catch exception!!, exception error is: {}".format(e.info()))



if __name__ == '__main__':

    x = 0
    _voip = PJSip()
    print('object',_voip)
    _voip.setupAccount('192.168.2.1','220','Swisscom10%')
    _voip.callNumber('0795678728')
   # _voip.StartCall()

