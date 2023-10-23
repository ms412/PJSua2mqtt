import pjsua2 as pj
#from utils import sleep4PJSUA2, handleErr
from datetime import datetime
import traceback
import sys
#import utils

isquit = False

def quitPJSUA():
    isquit = True

def sleep4PJSUA2(t):
    """sleep for a perid time, it takes care of pjsua2's threading,
    if the isquit is True, this function would immediately quit.

    Args:
        t (int): The time(second) you wants to sleep.
            if t equal -1, then it would sleep forever.
    """

    global isquit

    start = datetime.now()
    end = start
    while True:
        end = datetime.now()
        if ((end - start).total_seconds() >= t and t != -1) or isquit:
            print('Down')
            break
        pj.Endpoint.instance().libHandleEvents(20)

    return (end - start).total_seconds()

def handleErr(e: pj.Error, stopImmed=True):
    """handle the error, it would print pj error and exit the PJSUA
        Args:
            e: pj.Error
            stopImmed (Float): whether you wants to stop immediately, default is True
    """
    print("Exception {}\r\n, Traceback:\r\n".format(e.info()))
    traceback.print_exception(*sys.exc_info())
    if stopImmed:
        quitPJSUA()

class Call(pj.Call):
    """
    Call class, High level Python Call object, derived from pjsua2's Call object.
    there are Call class reference: https://www.pjsip.org/pjsip/docs/html/classpj_1_1Call.htm
    We may wants to implement our Call object to handle the "outgoing" call implement logic
    """

    def __init__(self, acc, peer_uri='', chat=None, call_id=pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, acc, call_id)
        self.acc = acc
        self.wav_player = None

    # override the function at original parent class
    # parent class's function can be called by super().onCallState()
    def onCallState(self, prm):
        ci = self.getInfo()
        print("*** Call: {} [{}]".format(ci.remoteUri, ci.lastStatusCode))

    def onCallMediaState(self, prm):
        # Deprecated: for PJSIP version 2.8 or earlier
        # ci = self.getInfo()
        # for mi in ci.media:
        #     if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
        #         (mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE or
        #          mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD):
        #         m = self.getMedia(mi.index)
        #         am = pj.AudioMedia.typecastFromMedia(m)
        #         # connect ports
        #         ep.Endpoint.instance.audDevManager().getCaptureDevMedia().startTransmit(am)
        #         am.startTransmit(
        #             ep.Endpoint.instance.audDevManager().getPlaybackDevMedia())
        aud_med = None
        try:
            # get the "local" media
            aud_med = self.getAudioMedia(-1)
            print('Aud_med', aud_med)
        except pj.Error as e:
            print("exception!!: {}".format(e.args))
            handleErr(e)

        if not self.wav_player:
            self.wav_player = pj.AudioMediaPlayer()
            try:
                self.wav_player.createPlayer("./input.16.wav")
            except pj.Error as e:
                del self.wav_player
                self.wav_player = None
                handleErr(e)

        if self.wav_player:
            self.wav_player.startTransmit(aud_med)


def enumLocalMedia(ep):
    # important: the Endpoint::mediaEnumPorts2() and Call::getAudioMedia() only create a copy of device object
    # all memory should manage by developer
    print("enum the local media, and length is ".format(len(ep.mediaEnumPorts2())))
    for med in ep.mediaEnumPorts2():
        # media info ref: https://www.pjsip.org/pjsip/docs/html/structpj_1_1MediaFormatAudio.htm
        med_info = med.getPortInfo()
        print("id: {}, name: {}, format(channelCount): {}".format(
            med_info.portId, med_info.name, med_info.format.channelCount))


def makeCall(id)
def main():
    ep = None
    try:
        ep = None

        # init the lib
        ep = pj.Endpoint()
        ep.libCreate()
        ep_cfg = pj.EpConfig()
        # Debug
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
        acc_cfg.idUri = 'sip:220@192.168.2.1'

        print("*** start sending SIP REGISTER ***")
        acc_cfg.regConfig.registrarUri = 'sip:192.168.2.1'

        # if there needed credential to login, just add following lines
        cred = pj.AuthCredInfo("digest", "*", '220', 0, 'Swisscom10%')
        acc_cfg.sipConfig.authCreds.append(cred)

        acc = pj.Account()
        acc.create(acc_cfg)

        ep.libStart()
        print("*** PJSUA2 STARTED ***")

        # use null device as conference bridge, instead of local sound card
        pj.Endpoint.instance().audDevManager().setNullDev()

        call = Call(acc)
        prm = pj.CallOpParam(True)
        prm.opt.audioCount = 1
        prm.opt.videoCount = 0
        call.makeCall('sip:0795678728@192.168.2.1:5060', prm)

        # hangup all call after 40 sec
        sleep4PJSUA2(10)

        print("*** PJSUA2 SHUTTING DOWN ***")
        del call
        del acc

    except KeyboardInterrupt as e:
        print("Catch the KeyboardInterrupt, exception error is: {}".format(e.args))

    # close the library
    try:
        ep.libDestroy()
    except pj.Error as e:
        handleErr(e)


if __name__ == '__main__':
    main()