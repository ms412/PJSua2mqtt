import pjsua2 as pj
import time



# Subclass to extend the Account and get notifications etc.
class MyAccount(pj.Account):
    def onRegState(self, prm):
        print("***OnRegState: " + prm.reason)

# pjsua2 test function
def pjsua2_test():
    # Create and initialize the library
    ep_cfg = pj.EpConfig()
    ep = pj.Endpoint()
    ep.libCreate()
    ep.libInit(ep_cfg)

    # Create SIP transport. Error handling sample is shown
    sipTpConfig = pj.TransportConfig()
    sipTpConfig.port = 5070
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig)
    # Start the library
    ep.libStart()

    acfg = pj.AccountConfig()
  #  acfg.idUri = "sip:test@sip.pjsip.org";
    acfg.idUri = '220@192.168.2.1'
   # acfg.regConfig.registrarUri = 'sip:192.168.2.1'
    cred = pj.AuthCredInfo("digest", "*", "220", 0, "Swisscom10%")
    #acfg.regConfig.registrarUri = "sip:sip.pjsip.org";
   # cred = pj.AuthCredInfo("digest", "*", "test", 0, "pwtest");
    acfg.sipConfig.authCreds.append( cred )
    # Create the account
    acc = MyAccount()
    acc.create(acfg)
    # Here we don't have anything else to do..
    time.sleep(10)

    # Destroy the library
    ep.libDestroy()

#
# main()
#
if __name__ == "__main__":
    pjsua2_test()