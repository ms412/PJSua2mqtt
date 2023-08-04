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
__VERSION__ = "0.1"
__DATE__ = "31.07.2023"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2023 Markus Schiesser"
__license__ = 'GPL v3'

import sys
import os
import time
import json
import logging
from configobj import ConfigObj
from library.mqttclientV2 import mqttclient
from library.logger import loghandler
from library.sungrowWebsocket import SungrowWS

class Pjsua2mqtt(object):

    def __init__(self, configfile='Sungrow2mqtt.config'):
        #    threading.Thread.__init__(self)

        self._configfile = os.path.join(os.path.dirname(__file__), configfile)
       # print(self._configfile)

        self._configBroker = None
        self._configLog = None
        self._configTrunk = None
        self._configTTS = None

        self._mqtt = None

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

    def startMqttBroker(self):
        self._log.debug('Methode: startMqtt()')
        self._mqtt = mqttclient(self._rootLoggerName)

        _host = self._BrokerConfig.get('HOST', 'localhost')
        _port = self._BrokerConfig.get('PORT', 1883)

        _state = False
        while not _state:
            _state = self._mqtt.connect(_host, _port)
            if not _state:
                self._log.error('Failed to connect to broker: %s', _host)
                time.sleep(5)

        self._log.debug('Sucessful connect to broker: %s', _host)

        return True

    def publishUpdate(self,data):
        self._log.debug('Send Update State')
        _topic = self._BrokerConfig.get('PUBLISH','/SMARTHOME/DEFAULT')

       # _topic = _configTopic + '/' + 'SYSTEM_STATE'
        #self._log.info('SYSTEM_STATE: %s'%(self._systemState))
        self._mqtt.publish(_topic, data)

        return True

    def startSip(self):
        self._log.debug('Methode: startSip()')
        if not None in self._TrunkConfig:
            _host = self._TrunkConfig('HOST','192.168.2.1')
            _user = self._TrunkConfig('USER','220')
            _passwd = self._TrunkConfig.get('PASSWD','GEHEIM')

    def startSungrow(self):
        self._log.debug('Methode: startSungrow()')
        if not None in self._SungrowConfig:
            _host = self._SungrowConfig.get('HOST','192.168.2.81')
            self._sungrow = SungrowWS(_host,self._rootLoggerName)
            self._sungrow.connect()

    def queryData(self):

        _data =  self._sungrow.getData()

        if False in _data:
            self._log.error('Failed to query data, restart', _data)
            del self._sungrow
            self.startSungrow()
        else:
            self.publishUpdate(json.dumps(_data))

        return True

        self._sungrow.getData()

    def start(self):
        self.readConfig()
        self.startLogger()
        self.startMqttBroker()
        self.startSungrow()
        while(True):
            self.queryData()
            time.sleep(15)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile = './Pjsua2mqtt.config'

    pj = Pjsua2mqtt(configfile)
    pj.start()