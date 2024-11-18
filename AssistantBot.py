import os
import subprocess
import pyttsx3
import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QCheckBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from googlesearch import search
import pyjokes
from googlesearch import search
import wikipedia
import webbrowser
import sys
from datetime import datetime
import re  # Import regex for extracting numbers from commands
from PyQt5.QtCore import QTimer
import pytz
from timezonefinder import TimezoneFinder
import threading
from geopy.geocoders import Nominatim
import requests
import re
import pyautogui #pip install pyautogui
from googlesearch import search
import tkinter as tk

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Global variable to control voice output
voice_enabled = True  # Default is voice enabled

# Initialize a flag to check if speech is already running
is_speaking = False

# Function to speak out text
def speak(audio, window=None):
    global is_speaking

    if not is_speaking:  # Check if the engine is not already speaking
        is_speaking = True

        def speak_thread():
            engine.say(audio)
            engine.runAndWait()
            global is_speaking  # Make sure to modify the global variable in the thread
            is_speaking = False  # Reset flag once speaking is done

        # Run the speaking task in a separate thread to avoid blocking the main thread
        threading.Thread(target=speak_thread).start()

    if window:
        window.output_box.append(f"AutoBot: {audio}")

# Listen function to convert speech to text
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"You said: {query}\n")
        return query
    except Exception as e:
        print(e)
        speak("I didn't catch that. Please say it again.")
        return "none"

# Function to get weather information from OpenWeatherMap
def get_weather(location, window=None):
    api_key = "a94ca53fe2645190deaf42f1bdff9b72"  # Replace with your OpenWeatherMap API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"

    try:
        # Make a request to the OpenWeatherMap API
        response = requests.get(base_url)
        data = response.json()

        # Debug: Print the full response data
        print(f"API response data: {data}")

        # Check if the request was successful (status code 200)
        if data["cod"] != 200:
            return f"Sorry, I couldn't retrieve the weather information for {location}. Please try again later."

        # Extract weather data
        city = data["name"]
        country = data["sys"]["country"]
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]

        # Build the weather report
        weather_report = (
            f"The current weather in {city}, {country} is {weather_description}. "
            f"The temperature is {temperature}°C, humidity is {humidity}%, and wind speed is {wind_speed} m/s."
        )

        return weather_report
    except requests.exceptions.RequestException as e:
        print(f"Error while making the API request: {str(e)}")
        return f"An error occurred while fetching the weather data: {str(e)}"
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Something went wrong: {str(e)}"

# Function to get the current time and date in a specific location
def get_time_and_date_in_location(location):
    # Initialize timezone finder
    tz_finder = TimezoneFinder()

    # Geocode the location (find the lat/long of the place)
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="auto_bot")
    location_info = geolocator.geocode(location)

    if location_info:
        latitude, longitude = location_info.latitude, location_info.longitude
        print(f"Latitude: {latitude}, Longitude: {longitude}")

        # Get the timezone for the given coordinates
        timezone_str = tz_finder.timezone_at(lng=longitude, lat=latitude)
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            time_in_location = datetime.now(tz).strftime("%H:%M:%S")
            date_in_location = datetime.now(tz).strftime("%A, %B %d, %Y")

            # Clean up location name (extract city or main part)
            location_name = location_info.address.split(",")[0]  # Get the city/country or main part of the address

            return f"The current time in {location_name} is {time_in_location}, and today's date is {date_in_location}."
        else:
            return f"Sorry, I couldn't determine the timezone for {location_info.address}."
    else:
        return "Sorry, I couldn't find the location. Please provide a valid city or country name."


# Wikipedia search function to get a short summary
def get_wikipedia_summary(query):
    try:
        # Fetch the summary of the page related to the query
        summary = wikipedia.summary(query, sentences=2)  # Limit the result to 2 sentences
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        # If there are multiple possible meanings for the query, choose the first one
        return f"Multiple results found, please be more specific. Options: {', '.join(e.options[:3])}"  # Show first 3 options
    except wikipedia.exceptions.HTTPTimeoutError:
        return "Sorry, I couldn't fetch information right now. Please try again later."
    except wikipedia.exceptions.RedirectError:
        return "Sorry, there was an issue fetching the page. It may have been redirected."
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find a page matching that query."
    except Exception as e:
        return f"An error occurred: {str(e)}"

from googlesearch import search

def google_search(query):
    try:
        # Collect search results in a list
        search_results = []
        for url in search(query, num_results=5):  # Fetch top 5 results
            search_results.append(url)
        
        # Format the results as a string
        response = f"Here are the top search results for {query}:\n" + "\n".join(search_results)
        return response
    except Exception as e:
        print(f"Error during Google search: {str(e)}")
        return "Sorry, I couldn't complete the search. Please try again."

google_keywords = ["search for", "find", "google"]

# Execute system command
def execute_command(command, window=None):
    command = command.lower()  # Ensure command is in lowercase for easier parsing
    
    # Check for volume up or down by specific percentage
    if 'volume' in command and ('increase' in command or 'decrease' in command):
        # Extract percentage from command
        match = re.search(r'\b\d{1,3}\b', command)
        if match:
            percentage = int(match.group())
            # Make sure percentage is between 1 and 100
            if 1 <= percentage <= 100:
                volume_change = int(65535 * (percentage / 100))  # Calculate the nircmd volume units
                if 'increase' in command:
                    speak(f"Increasing volume by {percentage} percent.", window)
                    subprocess.run(["C:\\Windows\\System32\\nircmd.exe", "changesysvolume", str(volume_change)])
                elif 'decrease' in command:
                    speak(f"Decreasing volume by {percentage} percent.", window)
                    subprocess.run(["C:\\Windows\\System32\\nircmd.exe", "changesysvolume", f"-{volume_change}"])
                return
            else:
                speak("Please specify a percentage between 1 and 100.", window)
                return
        else:
            # If no specific percentage is mentioned, decrease by 10% (default)
            if 'decrease' in command:
                speak("Decreasing volume by 10 percent.", window)
                subprocess.run(["C:\\Windows\\System32\\nircmd.exe", "changesysvolume", "-6553"])  # 10% decrease
            # If no specific volume action is mentioned, increase by 10% (default)
            elif 'increase' in command:
                speak("Increasing volume by 10 percent.", window)
                subprocess.run(["C:\\Windows\\System32\\nircmd.exe", "changesysvolume", "6553"])  # 10% increase
            return

# Respond to user mood
def respond_to_mood(mood, window=None):
    mood = mood.lower()
    response = "I'm here to listen. What's on your mind?"
    if 'good' in mood:
        response = "That's great to hear! Anything I can help with today?"
    elif 'bad' in mood or 'sad' in mood:
        response = "I'm sorry to hear that. I'm here if you need me."
    speak(response, window)
    if window:
        window.output_box.append(f"AutoBot: {response}")

# YouTube search function
def open_youtube(query, window=None):
    search_term = query.replace('play', '').replace('watch', '').strip()
    if search_term:
        url = f"https://www.youtube.com/results?search_query={search_term}"
        webbrowser.open(url)
        speak(f"Opening YouTube search results for {search_term}", window)

# Updated Greeting Function
def wishings(window=None):
    hour = int(datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning Boss. How can I help You?", window)
    elif hour >= 12 and hour < 17:
        speak("Good Afternoon Boss. How can I help You?", window)
    elif hour >= 17 and hour < 21:
        speak("Good Evening Boss. How can I help You?", window)
    else:
        speak("Good Night Boss. How can I help You?", window)

# Load the user's name if it exists
def load_name():
    if os.path.exists("user_name.txt"):
        with open("user_name.txt", "r") as file:
            return file.read().strip()
    else:
        return None 

# Save the user's name to a file
def save_name(name):
    with open("user_name.txt", "w") as file:
        file.write(name)

# Handle the location-based queries (e.g., where is India located?)
def handle_location_query(query, window=None):
    query = query.lower()

    # Check if the query contains "where is"
    if "where is" in query:
        place = query.replace("where is", "").strip()
        if place:
            response = get_wikipedia_summary(place)
            speak(response, window)
            if window:
                window.output_box.append(f"AutoBot: {response}\n")
        else:
            speak("Please specify a place you're asking about.", window)
    else:
        speak("I'm sorry, I can only help with location-based queries like 'Where is India located?'", window)

# Main handler for queries
def handle_query(query, window=None):
    original_query = query
    query = query.lower()

    if window:
        window.output_box.append(f"You said: {original_query}\n")

    # Check if user wants to quit
    if "quit" in query:
        speak("Goodbye! Closing the application.", window)
        QApplication.quit()  # Quit the application
        return

    # Check if user wants to set their name
    if "my name is" in query:
        name = query.replace("my name is", "").strip()
        if name:
            save_name(name)
            speak(f"Okay, {name}, I’ll remember that.", window)
            if window:
                window.output_box.append(f"AutoBot: Okay, {name}, I’ll remember that.\n")
            return

    elif "what is my name" in query or "who am i" in query:
        name = load_name()
        if name:
            response = f"Your name is {name}."
        else:
            response = "I don't know your name yet. You can tell me by saying 'My name is [Your Name]'."
        speak(response, window)
        if window:
            window.output_box.append(f"AutoBot: {response}\n")
        return

    if any(op in query for op in ['+', '-', '*', '/', '%']):
        try:
            result = eval(query)
            response = f"The result is {result}"
            speak(response, window)
            if window:
                window.output_box.append(f"AutoBot: {response}\n")
            return
        except Exception:
            response = "Sorry, I couldn't calculate that."
            speak(response, window)
            if window:
                window.output_box.append(f"AutoBot: {response}\n")
            return

    # Handle moods
    elif any(mood in query for mood in ['good', 'bad', 'happy', 'sad']):
        respond_to_mood(query, window)

    elif 'hello' in query or 'hi' in query or 'hey' in query:
        wishings(window)  # Call the new greeting function

    elif 'play' in query or 'watch' in query:
        open_youtube(query, window)

    elif 'tell me a joke' in query:
        joke = pyjokes.get_joke()
        speak(joke, window)
        if window:
            window.output_box.append(f"AutoBot: {joke}\n")
    
    elif "screenshot" in query:
        try:
            # Define the file path where the screenshot will be saved
            screenshot_path = r"C:\Users\OM\Pictures\Screenshots\screenshot.jpg"  # Make sure the extension is included
            # Capture screenshot using pyautogui
            im = pyautogui.screenshot()
            # Save the screenshot to the defined file path
            im.save(screenshot_path)
            speak(f"Screenshot taken and saved", window)
            if window:
                window.output_box.append(f"AutoBot: Screenshot taken and saved\n")
            return
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            speak(f"Sorry, there was an error taking the screenshot: {str(e)}", window)
            if window:
                window.output_box.append(f"AutoBot: Error taking screenshot: {str(e)}\n")
            return
        
 # Check if the query asks for weather
    if "weather" in query or "temperature" in query or "forecast" in query:
        # Improved regex to handle queries like "weather in Paris", "temperature in New York", etc.
        match = re.search(r'(weather|temperature|forecast) in ([\w\s]+)', query)
        if match:
            location = match.group(2).strip()  # Extract the location name
            print(f"Location extracted: {location}")  # Debug print to check the location
            weather_report = get_weather(location, window)
            speak(weather_report, window)
            if window:
                window.output_box.append(f"AutoBot: {weather_report}\n")
        else:
            speak("Please specify a city or country to get the weather information.", window)
            if window:
                window.output_box.append("AutoBot: Please specify a city or country to get the weather information.\n")
        return

     # Check if the query is asking about something ambiguous like "What is" or "Who is"
    if "what is" in query or "who is" in query or "who was" in query or "who was" in query:
        response = get_wikipedia_summary(query)
        speak(response, window)
        if window:
            window.output_box.append(f"AutoBot: {response}\n")
        return
    
    # for Google searches
    if any(keyword in query.lower() for keyword in google_keywords):
    # Strip out the keyword to get the main search query
        for keyword in google_keywords:
            query = query.lower().replace(keyword, '').strip()
    
        # Perform the Google search
        response = google_search(query)  # Get the search results as a string
    
        # Speak a concise summary
        speak(f"Here are the top search results for {query}", window)
    
        # Display the full results in the chatbot window
        if window:
            window.output_box.append(f"AutoBot: {response}\n")
        return

    # Handle queries for time and date in a location
    if "what time is it in" in query or "time in"in query:
        location = query.replace("what time is it in", "").strip()
        if location:
            response = get_time_and_date_in_location(location)  # Use the updated function
            speak(response, window)
            if window:
                window.output_box.append(f"AutoBot: {response}\n")
            return

    # Now we can safely ignore the fallback here because we already responded above
    elif "sorry" in query or query == "":
        return  # Do nothing here if we already responded

    # Handle location-based queries like "Where is [place] located?"
    if "where is" in query or "where was" in query:
        handle_location_query(query, window)
        return

    elif 'volume' in query:
        execute_command(query, window)

    elif 'open' in query:
        if 'youtube' in query:
            speak("Opening YouTube", window)
            webbrowser.open("https://www.youtube.com")
        elif 'chrome' in query:
            speak("Opening Google Chrome", window)
            os.system('start chrome')  # Open Chrome browser
            return
        elif 'notepad' in query:
            speak("Opening Notepad", window)
            os.system('start notepad')  # Open notepad 
            return
        elif 'spotify' in query:
            speak("Opening spotify", window)
            os.system('start spotify')  # Open spotify
            return
        elif 'telegram' in query:
            speak("Opening telegram", window)
            os.system('start telegram')  # Open telegram
            return  
        elif 'vscode' in query:
            speak("Opening vscode", window)
            os.system('start vscode')  # Open vscode
            return
        elif 'capcut' in query:
            speak("Opening capcut", window)
            os.system('start capcut')  # Open capcut
            return
 
    # Open website command (e.g. "open google", "open https://google.com")
    if "open" in query and "website" in query:
        website_name = query.replace("open", "").replace("website", "").strip()  # Extract website name
        if website_name:
            # Common domain extensions
            domain_extensions = [".com", ".org", ".net", ".edu", ".gov", ".in", ".ac", ".co", ".co.uk"]
            
            # Check if the website name ends with a known domain extension
            if any(website_name.endswith(ext) for ext in domain_extensions):
                # Prepend 'https://' if no protocol is given
                if not website_name.startswith('http://') and not website_name.startswith('https://'):
                    website_name = f"https://{website_name}"

            # Open the website in a browser
            webbrowser.open(website_name)
            speak(f"Opening {website_name}.", window)
        else:
            speak("Please specify the website you want to open.", window)
        return
    
    if "close" in query and "app" in query:
        app_name = query.replace("close", "").replace("app", "").strip()
        if app_name:
            if app_name.lower() == "notepad":
                os.system('taskkill /f /im notepad.exe')  # Close Notepad
                speak(f"Closing {app_name}.", window)
            elif app_name.lower() == "chrome":
                os.system('taskkill /f /im chrome.exe')  # Close Chrome
                speak(f"Closing {app_name}.", window)
            elif app_name.lower() == "spotify":
                os.system('taskkill /f /im spotify.exe')  # Close Chrome
                speak(f"Closing {app_name}.", window)
            elif app_name.lower() == "vscode":
                os.system('taskkill /f /im code.exe')  # Close Chrome
                speak(f"Closing {app_name}.", window)
            elif app_name.lower() == "capcut":
                os.system('taskkill /f /im CapCut.exe')  # Close Chrome
                speak(f"Closing {app_name}.", window)
            elif app_name.lower() == "telegram":
                os.system('taskkill /f /im Telegram.exe')  # Close Chrome
                speak(f"Closing {app_name}.", window)
            else:
                speak(f"Sorry, I don't know how to close {app_name}.", window)
        else:
            speak("Please specify which app you want to close.", window)
        return

    elif 'shutdown pc' in query or 'shut down the pc' in query:
        os.system('shutdown /s /t 5')  # Adjust the timer as needed (5 seconds here)
        speak("Shutting down the PC in a moment.",window)
        return

    elif 'restart pc' in query or 'Restart the pc' in query:
        os.system('shutdown /r /t 5')  # Adjust the timer as needed (5 seconds here)
        speak("Restarting the PC in a moment.",window)
        return
    
    elif 'sleep pc' in query or 'put the pc to sleep' in query:
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        speak("Putting the PC to sleep.",window)
        return

    elif 'lock pc' in query or 'lock the pc' in query:
        os.system('rundll32.exe user32.dll,LockWorkStation')
        speak("Locking the PC.",window)
        return

    else:
        speak("Sorry, I didn't understand that. Can you please repeat?", window)

# PyQt5 GUI
from PyQt5.QtCore import QTimer  # Ensure this import is at the top of your script
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import sys

class AssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoBot Assistant")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.output_box = QTextEdit(self)
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont("Arial", 12))
        layout.addWidget(self.output_box)

        self.input_box = QLineEdit(self)
        self.input_box.setFont(QFont("Arial", 12))
        layout.addWidget(self.input_box)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setFont(QFont("Arial", 12))
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

        self.voice_button = QPushButton("Listen", self)
        self.voice_button.setFont(QFont("Arial", 12))
        self.voice_button.clicked.connect(self.on_voice_button_click)
        layout.addWidget(self.voice_button)

        self.mood_checkbox = QCheckBox("Enable Voice Output", self)
        self.mood_checkbox.setChecked(True)
        self.mood_checkbox.stateChanged.connect(self.toggle_voice)
        layout.addWidget(self.mood_checkbox)

        self.setLayout(layout)

        self.input_box.setFocus()

        # Call greeting after window is fully shown
        QTimer.singleShot(0, self.init_assistant)  # Delay the greeting to avoid duplication

    def init_assistant(self):
        # Greet the user after the window is shown
        wishings(self)

    def on_submit(self):
        query = self.input_box.text().strip().lower()  # Convert to lowercase for easy matching
        self.input_box.clear()

        if query:
            # Check for the shutdown command
            if query == "shutdown":
                self.output_box.append("Shutting down... Goodbye")
                if self.mood_checkbox.isChecked():  # Check if voice output is enabled
                    speak("Shutting down... Goodbye")
                QTimer.singleShot(3000, self.close)  # Delay shutdown for 1 second to display message
            else:
                handle_query(query, self)

    def on_voice_button_click(self):
        query = listen_command()  # Listen for the command via microphone
        if query != "none":
            if query.strip().lower() == "shutdown":
                self.output_box.append("Shutting down... Goodbye")
                if self.mood_checkbox.isChecked():  # Check if voice output is enabled
                    speak("Shutting down... Goodbye!")
                QTimer.singleShot(3000, self.close)  # Delay shutdown for 1 second to display message
            else:
                handle_query(query, self)  # Handle the voice query

    def keyPressEvent(self, event):
        # If the Enter key is pressed, submit the query
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.on_submit()

    def toggle_voice(self):
        global voice_enabled
        voice_enabled = self.mood_checkbox.isChecked()


# Running the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.show()
    sys.exit(app.exec_())
