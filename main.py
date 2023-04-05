import json
import threading

import pyautogui
import pywhatkit
import pywinauto
import speech_recognition as sr
import pyttsx3
import openai
import webbrowser
from youtubesearchpython import VideosSearch, SearchVideos

import os

openai.api_key = "your api key"


def generate_response(user_input):
    conversation = ""
    user_name = "Moncef"
    bot_name = "Beryl"

    prompt = user_name + ":" + user_input + "\n" + bot_name + ":"
    conversation += prompt

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=conversation,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    response_str = response["choices"][0]["text"].replace("\n", "")
    response_str = response_str.split(user_name + ":", 1)[0].split(bot_name + ":", 1)[0]

    conversation += response_str + "\n"
    return response_str


def runchatbot(callback):
    s = ""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(voice.name)
        if voice.name == 'Microsoft David Desktop - English (United States)':
            engine.setProperty('voice', voice.id)
            break

    r = sr.Recognizer()
    mic = sr.Microphone(device_index=1)

    while True:
        with mic as source:
            print("\n Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)
        print("no longer listening")

        try:
            user_input = r.recognize_google(audio)
        except:
            continue

        if "play" in user_input:
            search_term = user_input.split("play ", 1)[1]
            print("Searching for:", search_term)

            try:
                search_results = SearchVideos(search_term, offset=1, mode="json", max_results=1).result()
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            search_results = json.loads(search_results)
            video_url = search_results["search_result"][0]["link"]

            webbrowser.open(video_url)
        if "stop" in user_input:

            windows = pyautogui.getWindowsAt(0, 0)
            # iterate over the windows and find the one you want
            for window in windows:
                if "Google Chrome" in window.title:
                    # activate the window
                    window.activate()

                    pyautogui.hotkey('ctrl', '9')
                    pyautogui.hotkey('space')

        else:
            print(".")

        response_str = generate_response(user_input)

        print(response_str)

        def say_response():
            engine.say(response_str)
            engine.runAndWait()

        # create a new thread to run the speech synthesis
        t = threading.Thread(target=say_response)
        t.start()
        callback(response_str)



