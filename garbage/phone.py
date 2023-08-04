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


__app__ = "Sip2Mqtt"
__VERSION__ = "0.1"
__DATE__ = "07.07.2023"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2023 Markus Schiesser"
__license__ = 'GPL v3'

import pjsua as pj
import logging
import time
import threading
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



class Voip:

    def __init__(self,callback):
  #  def __init__(self,callback,root_logger):
      #  self._calbackk = callback


        self.notification_cb = callback

    class CallCallback(pj.CallCallback):

       # def __init__(self, call=None):
        #    pjsua.CallCallback.__init__(self, call)
        def __init__(self, notification, call=None):
            pj.CallCallback.__init__(self, call)

            print("Istanziata MyCallCallback", call)
            self._notification = notification

        # Notification when call state has changed
        def on_state(self):
            global current_call
            global in_call
            print(
                "ll with", self.call.info().remote_uri)
            print(
                "is", self.call.info().state_text)
            print(
                "last code =", self.call.info().last_code)
            print(
                "(" + self.call.info().last_reason + ")")
            print('Test', self.call.info())

            if self.call.info().state == pj.CallState.DISCONNECTED:
                current_call = None
                print(
                    'Current call is', current_call)

                in_call = False
            elif self.call.info().state == pj.CallState.CONFIRMED:
                # Call is Answred
                print(
                    "Call Answred")
                wfile = wave.open("message.wav")
                time = (1.0 * wfile.getnframes()) / wfile.getframerate()
                print
                str(time) + "ms"
                wfile.close()
                call_slot = self.call.info().conf_slot
                self.wav_player_id = pjsua.Lib.instance().create_player('message.wav', loop=False)
                self.wav_slot = pjsua.Lib.instance().player_get_slot(self.wav_player_id)
                pjsua.Lib.instance().conf_connect(self.wav_slot, call_slot)
                sleep(time)
                pjsua.Lib.instance().player_destroy(self.wav_player_id)
                self.call.hangup()
                in_call = False

        # Notification when call's media state has changed.
        def on_media_state(self):
            if self.call.info().media_state == pj.MediaState.ACTIVE:
                print(
                    "Media is now active")
            else:
                print(
                    "Media is inactive")

    class CallCallbackOld(pj.CallCallback):

        def __init__(self, notification, call=None):
            pj.CallCallback.__init__(self, call)

            print("Istanziata MyCallCallback")
            self._notification = notification

        # Notification when call state has changed
        def on_state(self):

            uri_to_call = self.call.info().remote_uri
            print("Call with %s is %s Last code=%s (%s)" % (uri_to_call,
                                                                   self.call.info().state_text,
                                                                   self.call.info().last_code,
                                                                   self.call.info().last_reason))
            if self.call.info().state == pj.CallState.DISCONNECTED:

                print('Dissconnected')

            elif self.call.info().state == pj.CallState.CALLING:
                print('Dailing')


            elif self.call.info().state == pj.CallState.CONFIRMED:
                print('Active')

            elif self.call.inof().state == pj.CallState.EARLY:
                print('Rinign')

            else:
                print('State',self.call.info().state)

        # Notification when call's media state has changed.
        def on_media_stateOld(self):

            if self.call.info().media_state == pj.MediaState.ACTIVE:
                print("Stopping ring tone....")

                call_slot = self.call.info().conf_slot
                pj.Lib.instance().conf_connect(call_slot, 0)
                pj.Lib.instance().conf_connect(0, call_slot)

                logger.debug("VOLUME INIZIALE:" + str(pj.Lib.instance().conf_get_signal_level(call_slot)))
                pj.Lib.instance().conf_set_rx_level(call_slot, 0.5)
                pj.Lib.instance().conf_set_tx_level(call_slot, 0.5)

        def on_media_state(self):
            if self.call.info().media_state == pjsua.MediaState.ACTIVE:
                print(
                    "Media is now active")
            else:
                print(
                    "Media is inactive")



    # Callback to receive events from account
    class MyAccountCallback(pj.AccountCallback):
        sem = None

        def __init__(self, notification, account=None):
            pj.AccountCallback.__init__(self, account)
            print('CAllback')
            self._notification = notification
            self.already_registered = False
            self.auto_answer_call = None

            self.REQUEST_TIMEOUT = 408
            self.FORBIDDEN = 403
            self.NOT_FOUND = 404
            self.OK = 200
            self.SERVICE_UNAVAILABLE = 503

        def wait(self):
            print('wait')
            self.sem = threading.Semaphore(0)
            self.sem.acquire()

        def on_reg_state(self):
            print('Reg', self.sem)
            if self.sem:
                print('print',self.account.info().reg_status)
                if self.account.info().reg_status >= 200:
                    self.sem.release()

        def on_reg_stateOld(self):
            print('Reg')
            logger.debug('\ncalled on reg status:%s' % self.account.info().reg_status)
            logger.debug('called on reg reason:%s\n' % self.account.info().reg_reason)
            logger.debug('on line text:%s' % self.account.info().online_text)
            logger.debug('account is registered?:%s' % self.account.info().reg_active)
            logging.info(
                    "SIP: Registration complete, status=" + str(self.account.info().reg_status) + " (" + str(
                        self.account.info().reg_reason) + ")")

            reg_status = self.account.info().reg_status

            if reg_status in [self.REQUEST_TIMEOUT, self.SERVICE_UNAVAILABLE]:
                self._notification(reg_status)

            elif reg_status == self.OK:
                self._notification(reg_status)

            else:
                self._notification(reg_status)

        def on_incoming_call(self, call):
            # Unless this callback is implemented, the default behavior is to reject the call with default status code.
            self._notification(call.info().remote_uri)

            current_call = call
            call_cb = VoipCallCallback(current_call)
            current_call.set_callback(call_cb)

        def registered(self):
            print('Registered')


    def log_cb(self,level, msg, msg_len):
        print ( '[%s] %s' % (time.ctime(), msg))

    class MyTest(object):
        def __init__(self):
            pass

    def init_(self):
        print('init')
        Voip.MyTest

    def init_libold(self,params):
        global logger
        # logging.getLogger("Voip").debug("\nCalled init_lib method!!!\n")
        # Create library instance
        # Create pjsua before anything else

      #  self._callback = callback

        _sipUsername = '220'
        _sipDomain = '192.168.2.1'
        _sipPassword = 'Swisscom10%'

        self._params = params

        ua = pj.UAConfig()
        ua.user_agent = __app__

        mc = pj.MediaConfig()
        mc.clock_rate = 8000

        acc = pj.AccountConfig()
        acc.id="sip:" + _sipUsername + "@" + _sipDomain
        acc.reg_uri = "sip:" + _sipDomain
        acc.auth_cred = [pj.AuthCred("*", _sipUsername, _sipPassword)]
        acc.allow_contact_rewrite = False

        try:
            self._pjLib = pj.Lib()
          #  self._pjLib.init(log_cfg=pj.LogConfig(level=4, callback=self.log_cb), media_cfg=mc, ua_cfg=ua)
            self._pjLib.init(log_cfg=pj.LogConfig(level=2, callback=self.log_cb))
            self._pjLib.set_null_snd_dev()
            self._pjLib.start(with_thread=True)
            self._pjLib.handle_events()
            print('TEST')

            #self._pjLib.create_account(acc)
         #   acc = self.lib.create_account(acc, cb=VoipBackend.MyAccountCallback(self.notification_cb))
            _x = self._pjLib.create_account(acc, cb=Voip.MyAccountCallback(self.notification_cb))
            print(_x)
            Voip.MyAccountCallback



        except pj.Error as e:
            print('Failed to Setup Lib')
            if self._pjLib != None:
                self._pjLib.destroy_lib()
            return False

    def make_call(self,acc,uri):
        try:
            print("Making call to", uri)
            return acc.make_call(uri, cb=Voip.CallCallback(self.notification_cb))
        except pj.Error as e:
            print("Exception: " + str(e))
            return None

    def init(self):
        lib = pj.Lib()
        lib.init(log_cfg=pj.LogConfig(level=4, callback=self.log_cb))
        lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(0))
        lib.set_null_snd_dev()
        lib.start()
        lib.handle_events()

        acc = lib.create_account(pj.AccountConfig("192.168.2.1", "220", "Swisscom10%"))

        acc_cb = Voip.MyAccountCallback(self.notification_cb,acc)
        acc.set_callback(acc_cb)
        acc_cb.wait()



        print("\n")
        print("Registration complete, status=", acc.info().reg_status, \
              "(" + acc.info().reg_reason + ")")
        print("\nPress ENTER to quit")
        sys.stdin.readline()


        lck = lib.auto_lock()
        lib.set_null_snd_dev()

        current_call = self.make_call(acc,'sip:0795678728@192.168.2.1:5060')

        del lck

        # wait for the call to end before shuting down
        while True:
            pass
        # sys.stdin.readline()
        lib.destroy()
        lib = None


if __name__ == '__main__':

    x = 0
    _voip = Voip(x)
    print('object',_voip)
    _voip.init()

