
import json
import threading
import pyaudio
import pyautogui
import pywhatkit
import pywinauto
import speech_recognition as sr
import pyttsx3
import openai
import webbrowser
from youtubesearchpython import VideosSearch, SearchVideos
import os
from llamaapi import LlamaAPI

import time






def generate_response(user_input,apikey):
    try: 
        openai.api_key = apikey
        conversation = ""
        user_name = "Sir"
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
    except:
         return "None"

def generate_solution(prompt,apikey):
         

        # Initialize the SDK
        llama = LlamaAPI(apikey)

        # Build the API request
        api_request_json = {
            "messages": [
                {"role": "user", "content": "your my personal voice assistant give me organized and thoughtfull answers  "},
                {"role": "user", "content": prompt},  # Add the prompt to the messages

            ],
          
            
            "stream": False,
            "function_call": "get_current_weather",
        }

        # Execute the Request
        try:
            response = llama.run(api_request_json)
            response_data = response.json()
            message_content = response_data['choices'][0]['message']['content']
            return message_content
        except Exception as e:
            if "api key invalid" in str(e).lower():
                print("API key invalid")
            else:
                print("An error occurred:", e)
            return "None"


def runchatbot(callback,apikey,lama):
    s = ""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print (apikey)
    for voice in voices:
        print(voice.name)

        if voice.name == 'Microsoft David Desktop - English (United States)':

            engine.setProperty('voice', voice.id)
            break
    def create_file(filename):
    # Extract directory path from the filename
        directory = os.path.dirname(filename)

        # Create the directory if it doesn't exist
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Create the file
        with open(filename, 'w') as file:
            # Optionally, write initial content to the file
            pass

    def read_file(filename):
        try:
            with open(filename, 'r') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            return "File not found."
        except Exception as e:
            return f"Error reading file: {str(e)}"

        # Modify your existing code to include reading file content
        
            

    def modify_code(file_path, response):
        try:
            # Save the AI response directly to the file
            with open(file_path, 'w') as file:
                file.write(response)
            print("Code modified successfully.")
        except Exception as e:
            print(f"Error modifying code: {str(e)}")

    def delete_file(filename):
        os.remove(filename)


    r = sr.Recognizer()
    mic = sr.Microphone(device_index=1)
    
    while True:
            try:
                with mic as source:
                    print("\nSleeping...")
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, timeout=5)
            except sr.WaitTimeoutError:
                print("Timeout occurred while listening.")
                continue
            except Exception as e:
                print("Error:", e)
                continue
            
            print("No longer sleeping")
            # Release the microphone resource
            
                
                
                        
                
            try:
                        user_input = r.recognize_google(audio)
                        print(user_input)
            except sr.UnknownValueError:
                        continue
            if "slave" in user_input or "hey" in user_input or "Hey" in user_input:

                def say_response():
                        engine.say("Yes My Lord !!")
                        engine.runAndWait()
                say_response()
                start_time = time.time()
                while True:
                    with mic as source:
                        print("\n Listening...")
                        try:
                            r.adjust_for_ambient_noise(source, duration=0.5)
                            audio = r.listen(source, timeout=5)
                        except sr.WaitTimeoutError:
                            print("Timeout occurred while listening.")
                            continue
                        except Exception as e:
                            print("Error:", e)
                            continue
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 15:
                        print("No longer listening (15 seconds elapsed)")
                        break
    
                    
           

                    try:
                        user_input = r.recognize_google(audio)
                        print(user_input)
                    except sr.UnknownValueError:
                        continue
                    if "read file" in user_input:
                        file_name_index = user_input.index("read file") + len("read file")
                        file_name = user_input[file_name_index:].strip()
                          # Extract the filename after "read file" command
                        def say_response():
                                engine.say("Yes My Lord Reading file!!")
                                engine.runAndWait()
                                
                        say_response()
                        while True:
                            with mic as source:
                                print("\n listening for modifs...")
                                try:
                                    r.adjust_for_ambient_noise(source, duration=0.5)
                                    audio = r.listen(source, timeout=5)
                                except sr.WaitTimeoutError:
                                    print("Timeout occurred while listening formodifs.")
                                    continue
                                except Exception as e:
                                    print("Error:", e)
                                    continue
                            print("no longer listening for modifs")
                            try:
                                user_input = r.recognize_google(audio)
                                print(user_input)
                            except sr.UnknownValueError:
                                        continue
                            
                            if "modify" in user_input:
                                content = read_file(file_name)
                                if content:
                                    user_input += " give only full and complete code modification based on your analysys ,dont explain" + content
                                    if lama==False :
                                        try:
                                            response_str = generate_response(user_input,apikey)
                                        except:
                                            continue
                                    else:
                                        try:
                                            response_str = generate_solution(user_input,apikey)
                                        except:
                                            continue
                                    print(response_str)
                                    modify_code(file_name_index,response_str)
                            if "go back" in user_input:
                                pyautogui.hotkey('ctrl', 'z')

                            if "close file"  in user_input :
                                    break
                            
                            print("Modification saved.")
                        break
                        
                    if "sleep"in user_input:
                        break
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
                        break
                    if "stop" in user_input:

                        windows = pyautogui.getWindowsAt(0, 0)
                        # iterate over the windows and find the one you want
                        for window in windows:
                            if "Google Chrome" in window.title:
                                # activate the window
                                window.activate()

                                pyautogui.hotkey('ctrl', '9')
                                pyautogui.hotkey('space')
                                break

                    else:
                        print(".")
                        if lama==False :
                            try:
                                response_str = generate_response(user_input,apikey)
                            except:
                                continue
                        else:
                            try:
                                response_str = generate_solution(user_input,apikey)
                            except:
                                continue
                        print(response_str)

                        def say_response():
                            engine.say(response_str)
                            engine.runAndWait()
                        try:
                            t = threading.Thread(target=say_response)
                            t.start()
                            
                            callback(response_str)
                        except:
                            continue
                        break
                # create a new thread to run the speech synthesis
            
                        



