import pyttsx3

engine = pyttsx3.init()
rate = engine.getProperty('rate')  # getting details of current speaking rate
print(rate)  # printing current voice rate
engine.setProperty('rate', 125)  # setting up new voice rate
voices = engine.getProperty('voices')
print(voices)
engine.setProperty('voice', voices[1].id)
engine.say("I will speak this text")
engine.runAndWait()