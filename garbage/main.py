# $Id: registration.py 2171 2008-07-24 09:01:33Z bennylp $
#
# SIP account and registration sample. In this sample, the program
# will block to wait until registration is complete
#
# Copyright (C) 2003-2008 Benny Prijono <benny@prijono.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#https://github.com/pjsip/pjproject
#https://docs.pjsip.org/en/latest/api/pjsua2/index.html
#https://github.com/alyssaong1/VoIPBot
# https://github.com/cristeab/autodialer
# https://github.com/MartyTremblay/sip2mqtt
#https://github.com/arnonym/ha-plugins
# https://github.com/crs4/most-voip

#https://github.com/pjsip/pjproject/tree/master/pjsip-apps/src/confbot
# https://github.com/pjsip/pjproject/tree/master/pjsip-apps/src/pygui
import sys
import pjsua as pj
import threading


def log_cb(level, str, len):
    print(str, end=' ')


class MyAccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()


# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        global current_call
        print("Call with", self.call.info().remote_uri, end=' ')
        print("is", self.call.info().state_text, end=' ')
        print("last code =", self.call.info().last_code, end=' ')
        print("(" + self.call.info().last_reason + ")")

      #  if self.call.info().state == pj.CallState.DISCONNECTED:
       #     current_call = None
        #    print('Current call is 2-', current_call)

    # Notification when call's media state has changed.
    def on_media_state(self):
        print('xxxxxx')
       # for media_index, media in enumerate(call_info.media)
        if self.call.info().media_state == pj.MediaState.ACTIVE:

            call_slot = self.call.info().conf_slot
            print("xxx", call_slot)

           # pj.Lib.instance().player_set_pos(call_slot, 0)
            #pj.Lib.instance().conf_disconnect(pj.Lib.instance().player_get_slot(call_slot), 0)

            # Connect the call to sound device
            pj.Lib.set_null_snd_dev()
          #  call_slot = self.call.info().conf_slot
           # pj.Lib.instance().conf_connect(call_slot, 0)
            #pj.Lib.instance().conf_connect(0, call_slot)
            print("Media is now active")

         #   pj.Lib.instance().conf_set_rx_level(call_slot, 0.5)
          #  pj.Lib.instance().conf_set_tx_level(call_slot, 0.5)
        else:
            print("Media is inactive")


# Function to make call
def make_call(uri):
    try:
        print("Making call to", uri)
        return acc.make_call(uri, cb=MyCallCallback())
    except pj.Error as e:
        print("Exception: " + str(e))
        return None


lib = pj.Lib()

try:
    lib.init(log_cfg=pj.LogConfig(level=3, callback=log_cb))
    lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(0))
    lib.start()

    acc = lib.create_account(pj.AccountConfig("192.168.2.1", "220", "Swisscom10%"))

    acc_cb = MyAccountCallback(acc)
    acc.set_callback(acc_cb)
    acc_cb.wait()

    print("\n")
    print("Registration complete, status=", acc.info().reg_status, \
          "(" + acc.info().reg_reason + ")")
    print("\nPress ENTER to quit")
    sys.stdin.readline()

    lck = lib.auto_lock()
    lib.set_null_snd_dev()
    codecs = lib.enum_codecs()
    print('codec',codecs)
    for codec in codecs:
        # adjust codecs priorities
        #codec_priority = codec.priority
        print('codec',codec.name)
        #if 'G729' in codec.name or 'PCMA' in codec.name:
        #    codec_priority = 255
        #    lib.set_codec_priority(codec.name, codec_priority)
    current_call = make_call('sip:0795678728@192.168.2.1:5060',MyCallCallback())

    # Create local/user-less account
  #  acc = lib.create_account_for_transport(transport)

    # Make call
   # call = acc.make_call(sys.argv[1], MyCallCallback())
    print('current call 3',current_call )
    del lck

    lib.destroy()
    lib = None

except pj.Error as e:
    print("Exception: " + str(e))
    lib.destroy()
