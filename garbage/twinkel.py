from pytwinkle import Twinkle


def callback(event, *args):
    if event == "registration_succeeded":
        uri, expires = args
        print("registratiom succeeded, uri: %s, expires in %s seconds" % (uri, expires))
        # The module keeps the session, you havent to register
        mTP.message("name@domain", "Hello")
        mTP.call("name@domain")

    if event == "new_msg":
        msg = args[0]
        print("new_msg!: " + str(msg))

    if event == "incoming_call":
        call = args[0]
        print("call: " + str(call))

    if event == "cancelled_call":
        line = args[0]
        print("call cancelled, line: %s" % (line))

    if event == "answered_call":
        call = args[0]
        print("answered: %s" % (str(call)))

    if event == "ended_call":
        line = args[0]
        print("call ended, line: %s" % (line))


mTP = Twinkle(callback)
mTP.set_account("220", "192.168.2.1", "Swisscom10%")
mTP.call('0795678728')
mTP.run()