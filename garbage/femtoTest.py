import femtosip
sip = femtosip.SIP("220", "Swisscom10%", "192.168.2.1", 5060, "Test")
sip.call('0795678728', 15.0)