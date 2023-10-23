#!/usr/bin/python3
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


__app__ = "SIP2MQTT"
__VERSION__ = "0.2"
__DATE__ = "20.10.2023"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2023 Markus Schiesser"
__license__ = 'GPL v3'

import sys
import os
import time
import json
import logging
from multiprocessing import Process, Queue, Pipe
from configobj import ConfigObj
from library.PJSip import PJSip
from library.mqttclientV2 import mqttclient
from library.logger import loghandler
from library.Text2Speach import Text2Speach


class Sip2mqtt(object):

    def __init__(self, configfile='Sungrow2mqtt.config'):
        #    threading.Thread.__init__(self)

        self._configfile = os.path.join(os.path.dirname(__file__), configfile)

        self._configBroker = None
        self._configLog = None
        self._configTrunk = None
        self._configTTS = None

        self._mqtt = None

        self._p_pipeIn, self._p_pipeOut = Pipe()

        self._rootLoggerName = __app__

    def readConfig(self):

        _config = ConfigObj(self._configfile)

        if bool(_config) is False:
            print('ERROR config file not found', self._configfile)
            sys.exit()
            # exit

        self._BrokerConfig = _config.get('BROKER', None)
        self._LoggerConfig = _config.get('LOGGING', None)
        self._TrunkConfig = _config.get('TRUNK', None)
        return True

    def startLogger(self):
        # self._log = loghandler('marantec')

        self._LoggerConfig['DIRECTORY'] = os.path.dirname(__file__)
        print(self._LoggerConfig)
        self._root_logger = loghandler(self._LoggerConfig.get('NAME', __app__))
        self._root_logger.handle(self._LoggerConfig.get('LOGMODE', 'PRINT'), self._LoggerConfig)
        self._root_logger.level(self._LoggerConfig.get('LOGLEVEL', 'DEBUG'))
        self._rootLoggerName = self._LoggerConfig.get('NAME', self.__class__.__name__)
        print(self._LoggerConfig)
        self._log = logging.getLogger(self._rootLoggerName + '.' + self.__class__.__name__)

        self._log.info('Start %s, %s' % (__app__, __VERSION__))

        return True

    def startMqttClient(self):
        self._log.debug('Methode: startMqttBroker() %s',self._BrokerConfig)
        self._mqtt = mqttclient(self._rootLoggerName)

        _host = self._BrokerConfig.get('HOST', 'localhost')
        _port = self._BrokerConfig.get('PORT', 1883)
      #  print(self._BrokerConfig.get('THREADING'),type(self._BrokerConfig.as_bool('THREADING')))
       # _threading = bool(self._BrokerConfig.as_bool('THREADING'))
       # print(_threading)

        _state = False
        while not _state:
            _state = self._mqtt.connect(_host, _port)
            if not _state:
                self._log.error('Failed to connect to broker: %s', _host)
                time.sleep(5)

        self._log.debug('Sucessfully connect to broker: %s', _host)

        _subscribe = self._BrokerConfig.get('SUBSCRIBE','/SMARTHOME/TEST') + '/#'
        (_result,_mid) = self._mqtt.subscribe(_subscribe, self.callbackMqtt)

        return True

    def publishMqtt(self,data):
        self._log.debug('Send Update State')
        _topic = self._BrokerConfig.get('PUBLISH','/SMARTHOME/DEFAULT')

        if self._mqtt is not None:
            self._mqtt.publish(_topic, json.dumps(data))

        return True

    def callbackMqtt(self,client,userdata,msg):
    #    print('callmeback1', client, userdata, msg)
        self._log.debug('mqttCallback: Topic ' + msg.topic + " QOS: " + str(msg.qos) + " Payload: " + str(msg.payload))
        _payload = {}
        _topic = msg.topic
       # try:
           # _payload = json.loads(msg.payload.decode())
        #_payload = json.loads(msg.payload)
        self._log.debug('Payload %s'% msg.payload)
        _number = msg.payload.decode("utf-8")

        x = json.loads(msg.payload)
        y = x["ID"]
        z = x['MSG']
        print(x,y,z)
        self.dailerSip(y,z)
        #except:
        self._log.error('brockerCallback evalutation of Mqtt message failed: %s'% str(msg.payload))

        return True

    def startSipClient(self,p_pipeIn):
        self._log.debug('Methode: startSip() with config %s'% self._TrunkConfig)

        if not None in self._TrunkConfig:
            _host = self._TrunkConfig.get('HOST','192.168.2.1')
            _user = self._TrunkConfig.get('USER','220')
            _passwd = self._TrunkConfig.get('PASSWD','GEHEIM')
        else:
            self._log.error('Trunk Configuration missing')

        try:
            self._sipClient = PJSip(self._rootLoggerName,p_pipeIn)
            self._sipClient.setNotification(self.callbackSip)
            self._sipClient.setupAccount('192.168.2.1', '220', 'Swisscom10%')
        except:
            self._log.error('Failed to start SIP Client')
            self._sipClient.shutdown()
            return False

        return True
    def dailerSip(self,number,message) -> bool:
        print('MSG',number,message)
        self.generateSpeach(message)
        self._p_pipeOut.send(number)
        return True

    def callbackSip(self,message):
        self._log.debug('sipCallback: message %s'% message)
      #  print(message)
        self.publishMqtt(message)

    def startText2Speach(self):
        self._tts = Text2Speach()
        self._tts.voice('de')

    def generateSpeach(self,text):
        path = self._tts.convert(text)

    def start(self):
        self.readConfig()
        self.startLogger()
        self.startText2Speach()
       # time.sleep(2)
      #  self.startSip()
        self.startMqttClient()
        time.sleep(10)

        self._p_sipClient = Process(target=self.startSipClient, args=(self._p_pipeIn,))
        self._p_sipClient.start()
        #time.sleep(5)


       # self.dailSip('0795678728',self.generateSpeach('Das ist ein Langer Test um zu sehen ob das funktioniert'))
        #self.dailSip('0795678728', 'Das ist ein Langer Test um zu sehen ob das funktioniert')
        while(True):
            if self._p_pipeOut.poll():
                self.callbackSip(self._p_pipeOut.recv())

        self._p_sipClient.join()
        self._p_pipeIn.close()
        self._p_pipeOut.close()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile = './sip2mqtt.config'

    pj = Sip2mqtt(configfile)
    pj.start()