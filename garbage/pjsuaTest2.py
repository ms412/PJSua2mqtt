

import pjsua2 as pj
import time

# https://github.com/efficacy38/pjsua2-test/blob/main/audioSimularity/client/client.py

class MyAccount(pj.Account):
    def onRegState(self, prm):
        print("***OnRegState: " + prm.reason)

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
            print('***CALLIJG***',ci.lastStatusCode)
        if ci.state == pj.PJSIP_INV_STATE_CONNECTING:
            print('***CONNECTING***',ci.lastStatusCode)
        if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            print('***CONFIRMED***',ci.lastStatusCode)
            print(ci.media,ci.media[0],ci.media.size)
            if ci.media[0].type == pj.PJMEDIA_TYPE_AUDIO:
                print('***AUDIO***')
            if ci.media[0].status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                print('***MEDIA ACTIVE***')
        if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            print('***DISCONNECTING***',ci.lastStatusCode)

    def onCallMediaState(self, prm):
      #  AudioMediaPlayer
       # player;
       # AudioMedia & speaker_media = Endpoint::instance().audDevManager().getPlaybackDevMedia();
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
        ci = self.getInfo()
        print('TEST',ci,prm)

       # for mi in ci.media:
        #    print(ci.media.size(),mi )
         #   if mi.type == pj.PJMEDIA_TYPE_AUDIO:
          #      print('pj.PJMEDIA_TYPE_AUDIO')
        #    if mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
        #        print('ACTIVE')
        #        m = self.getMedia(mi.index)
        #        am = pj.AudioMedia.typecastFromMedia(m)
        #             # connect ports
        #        ep.Endpoint.instance.audDevManager().getCaptureDevMedia().startTransmit(am)
        #        am.startTransmit(ep.Endpoint.instance.audDevManager().getPlaybackDevMedia())
       # print("enum the local media, and length is ".format(len(ep.mediaEnumPorts2())))

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
            handleErr(e)

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
                handleErr(e)
            else:
                print('Start playbacksss')
             #   self.wav_player.startTransmit(aud_med)
        if self.wav_player:
            print('play message')
            self.wav_player.startTransmit(aud_med)

    #  if args.record:
      #  if not self.wav_recorder:
       #     self.wav_recorder = pj.AudioMediaRecorder()
       #     try:
        #        self.wav_recorder.createRecorder("./recordered.wav")
         #   except pj.Error as e:
         #       print("Exception!!: failed opening recordered wav file")
          #      del self.wav_recorder
           #     self.wav_recorder = None
            #    handleErr(e)
          #  else:
           #     aud_med.startTransmit(self.wav_recorder)
#def enumLocalMedia(ep):
    # important: the Endpoint::mediaEnumPorts2() and Call::getAudioMedia() only create a copy of device object
    # all memory should manage by developer
 #   print("enum the local media, and length is ".format(len(ep.mediaEnumPorts2())))
  #  for med in ep.mediaEnumPorts2():
        # media info ref: https://www.pjsip.org/pjsip/docs/html/structpj_1_1MediaFormatAudio.htm
   #     med_info = med.getPortInfo()
    #    print("id: {}, name: {}, format(channelCount): {}".format(
     #       med_info.portId, med_info.name, med_info.format.channelCount))

def main():
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


    acc = MyAccount()
    acc.create(acc_cfg)
   # acc = pj.Account()
   # acc.create(acc_cfg)

    ep.libStart()
    print("*** PJSUA2 STARTED ***")

    # use null device as conference bridge, instead of local sound card
    pj.Endpoint.instance().audDevManager().setNullDev()

    calls=['sip:0795678728@192.168.2.1:5060']
    for item in calls:
        call = Call(acc)
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
    main()