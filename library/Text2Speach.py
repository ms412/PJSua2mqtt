
import time
import os
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment

'''
https://github.com/jiaaro/pydub#installation


# ffmpeg
apt-get install ffmpeg libavcodec-extra
'''



class Text2Speach(object):

    def __init__(self):
        self._lang = 'en'
        self._converter = pyttsx3.init()

    def voice(self,lang):
        self._lang = lang
        self._converter.setProperty('rate', 150)
        # Set volume 0-1
        self._converter.setProperty('volume', 0.7)

    def convertTTSx3(self,text):
        dir_name = 'temp'
        base_filename = 'announcement'
        filename_suffix = 'wav'
        filename = os.path.join(dir_name, base_filename + '.' + filename_suffix)
        print(filename)
        self._converter.save_to_file(text, filename)
        self._converter.runAndWait()
        return filename

    def convert(self,text):
        dir_name = 'temp'
        base_filename = 'announcement'
        filename_suffix = 'mp3'
        filename = os.path.join(dir_name, base_filename + '.' + filename_suffix)
        print(filename)
       # import time
        #timestamp = time.strftime("%Y%m%d-%H%M%S")
       # print (timestamp, os.path.dirname(os.path.realpath(__file__)))
        #filename = 'message'+ timestamp +'.wav'
        tts = gTTS(text,lang=self._lang,slow=False)
        tts.save(filename)
       # fullpath = os.path.dirname(os.path.abspath(filename)) + filename
        #print(filename)
        filename_suffix = 'wav'
        filename1 = os.path.join(dir_name, base_filename + '.' + filename_suffix)
        sound = AudioSegment.from_mp3(filename)
        sound.export(filename1, format="wav")
        return filename1

   # os.path.join(dir_name, base_filename + '.' + filename_suffix)
      #  dir_path = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":

    tts = Text2Speach()
   # tts.convert('hello world')
    tts.voice('de')
    tts.convert('Das ist ein Test')
