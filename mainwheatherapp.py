import tkinter as tk
import requests
import time
import speech_recognition as sr
import pyttsx3
import threading

# --- Voice Engine Setup ---
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('voice', engine.getProperty('voices')[1].id)  # Female voice if available

def speak(text):
    try:
        threading.Thread(target=lambda: engine.say(text) or engine.runAndWait()).start()
    except:
        pass

# --- Weather Fetching ---
def getWeather(event=None, city=None):
    if city is None:
        city = textField.get()

    api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=1eab01630132d9fdc8fb19c8a9516eb7"
    try:
        json_data = requests.get(api).json()
    except:
        error_label.config(text="⚠ Unable to fetch data. Check your internet.", fg="red")
        speak("Unable to fetch weather data. Check your internet connection.")
        return

    try:
        condition = json_data['weather'][0]['main']
        temp = int(json_data['main']['temp'] - 273.15)
        min_temp = int(json_data['main']['temp_min'] - 273.15)
        max_temp = int(json_data['main']['temp_max'] - 273.15)
        pressure = json_data['main']['pressure']
        humidity = json_data['main']['humidity']
        wind = json_data['wind']['speed']
        sunrise = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunrise'] - 21600))
        sunset = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunset'] - 21600))

        final_info = f"{condition}\n{temp}°C"
        final_data = (
            f"🌡 Min: {min_temp}°C   ⛅ Max: {max_temp}°C\n"
            f"🧭 Pressure: {pressure} hPa   💧 Humidity: {humidity}%\n"
            f"🍃 Wind: {wind} m/s\n"
            f"🌄 Sunrise: {sunrise}   🌅 Sunset: {sunset}"
        )

        label1.config(text=final_info)
        label2.config(text=final_data)
        error_label.config(text="")
        speak(f"The weather in {city} is {condition}. Temperature is {temp} degrees Celsius.")

    except:
        label1.config(text="")
        label2.config(text="")
        error_label.config(text="⚠ City not found. Please try again.", fg="red")
        speak("City not found. Please try again.")

# --- Function to get first working mic ---
def get_working_mic():
    mic_list = sr.Microphone.list_microphone_names()
    for i, name in enumerate(mic_list):
        try:
            with sr.Microphone(device_index=i) as source:
                return i  # first mic that works
        except:
            continue
    return None  # no working mic found

# --- Voice Input ---
def voiceInput():
    r = sr.Recognizer()
    mic_index = get_working_mic()

    if mic_index is None:
        error_label.config(text="⚠ No working microphone detected. Please type the city name.", fg="red")
        speak("No working microphone detected. Please type the city name.")
        return

    try:
        with sr.Microphone(device_index=mic_index) as source:
            error_label.config(text="🎤 Listening... Please say the city name.", fg="blue")
            speak("Please say the city name.")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)

        city = r.recognize_google(audio)
        textField.delete(0, tk.END)
        textField.insert(0, city)
        threading.Thread(target=lambda: getWeather(city=city)).start()

    except sr.UnknownValueError:
        error_label.config(text="⚠ Could not understand voice. Try again or type manually.", fg="red")
        speak("Sorry, I could not understand. Please type the city name.")
    except sr.RequestError:
        error_label.config(text="⚠ Speech service unavailable. Please type the city name.", fg="red")
        speak("Speech service unavailable. Please type the city name.")

# --- GUI Setup ---
canvas = tk.Tk()
canvas.geometry("720x650")
canvas.title("🌤 Weather Wizard")
canvas.configure(bg="#d0f0f7")

# --- Fonts ---
font_title = ("Helvetica", 26, "bold")
font_input = ("Helvetica", 20)
font_info = ("Helvetica", 16)
font_error = ("Helvetica", 14, "italic")

# --- Title ---
title = tk.Label(canvas, text="Weather Wizard", font=font_title, bg="#d0f0f7", fg="#004d40")
title.pack(pady=20)

# --- Input Field ---
textField = tk.Entry(canvas, justify='center', width=20, font=font_input, bg="#ffffff", fg="#00796b", bd=3, relief="ridge")
textField.pack(pady=10)
textField.focus()
textField.bind('<Return>', getWeather)

# --- Buttons Frame ---
btn_frame = tk.Frame(canvas, bg="#d0f0f7")
btn_frame.pack(pady=5)

# --- Search Button ---
def on_enter(e): search_btn.config(bg="#00796b", fg="white")
def on_leave(e): search_btn.config(bg="#b2dfdb", fg="#004d40")

search_btn = tk.Button(btn_frame, text="Search", command=getWeather, font=font_info, bg="#b2dfdb", fg="#004d40", relief="raised", bd=2)
search_btn.grid(row=0, column=0, padx=10)
search_btn.bind("<Enter>", on_enter)
search_btn.bind("<Leave>", on_leave)

# --- Voice Button ---
voice_btn = tk.Button(btn_frame, text="🎤 Speak", command=lambda: threading.Thread(target=voiceInput).start(), font=font_info, bg="#ffecb3", fg="#004d40", relief="raised", bd=2)
voice_btn.grid(row=0, column=1, padx=10)

# --- Error Label ---
error_label = tk.Label(canvas, font=font_error, bg="#d0f0f7", fg="red")
error_label.pack(pady=5)

# --- Weather Info Card ---
card_frame = tk.Frame(canvas, bg="#ffffff", bd=2, relief="groove")
card_frame.pack(pady=20, padx=30, fill="both", expand=True)

label1 = tk.Label(card_frame, font=("Helvetica", 28, "bold"), bg="#ffffff", fg="#00796b")
label1.pack(pady=20)

label2 = tk.Label(card_frame, font=font_info, bg="#ffffff", fg="#004d40", justify="center")
label2.pack(pady=10)

# --- Clean Exit for VS Code ---
def on_close():
    canvas.quit()
    canvas.destroy()
    exit()

canvas.protocol("WM_DELETE_WINDOW", on_close)
canvas.mainloop()