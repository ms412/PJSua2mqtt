from pyVoIP.VoIP import VoIPPhone, InvalidStateError


def answer(call):  # This will be your callback function for when you receive a phone call.
    try:
        call.answer()
        call.hangup()
    except InvalidStateError:
        pass


if __name__ == "__main__":
    phone =VoIPPhone("192.168.2.1","5060",220,"Swisscom10%",)
    "192.168.2.1", "220", "Swisscom10%"
    phone = VoIPPhone( < SIP
    Server
    IP >, < SIP
    Server
    Port >, < SIP
    Server
    Username >, < SIP
    Server
    Password >, callCallback = answer, myIP = < Your
    computer
    's local IP>, sipPort=<Port to use for SIP (int, default 5060)>, rtpPortLow=<low end of the RTP Port Range>, rtpPortHigh=<high end of the RTP Port Range>)
    phone.start()
    input('Press enter to disable the phone')
    phone.stop()