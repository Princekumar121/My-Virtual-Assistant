import speech_recognition as sr
import pyttsx3
import wikipedia
import datetime
import pywhatkit
import cv2


listener = sr.Recognizer() 
engine = pyttsx3.init()  
engine.setProperty('rate', 150)

def talk(text):
    """Speaks the given text using the text-to-speech engine."""
    engine.say(text)
    engine.runAndWait()

def load_iron_man_overlay():
    """Loads the Iron Man image for overlay."""
    iron_man_path = "images.jpeg"  
    iron_man_img = cv2.imread(iron_man_path, cv2.IMREAD_UNCHANGED)
    if iron_man_img is None:
        raise FileNotFoundError(f"Image not found at path: {iron_man_path}")
    if iron_man_img.shape[2] == 3:  
        iron_man_img = cv2.cvtColor(iron_man_img, cv2.COLOR_BGR2BGRA)
    return iron_man_img

def resize_overlay(overlay, frame):
    """Resizes the overlay image proportionally to the frame (optional)."""
    overlay_height, overlay_width, channels = overlay.shape
    frame_height, frame_width, _ = frame.shape

    scale_factor = 0.3  
    new_overlay_width = int(overlay_width * scale_factor)
    new_overlay_height = int(overlay_height * scale_factor)

    resized_overlay = cv2.resize(overlay, (new_overlay_width, new_overlay_height))
    return resized_overlay

def overlay_iron_man_face(frame, overlay):
    """Overlays the Iron Man face image onto the video frame."""
    overlay_height, overlay_width, channels = overlay.shape
    frame_height, frame_width, _ = frame.shape

    x_offset = int((frame_width - overlay_width) / 2)
    y_offset = int(frame_height * 0.1)  

    for y in range(overlay_height):
        for x in range(overlay_width):
            if overlay[y, x, 3] > 0:  
                frame[y + y_offset, x + x_offset] = overlay[y, x, :3]

    return frame    

def get_command():
    """Listens for user input, displays Iron Man overlay, and returns the recognized speech."""
    cap = cv2.VideoCapture(0)  # Capture video from webcam

    try:
        iron_man_overlay = load_iron_man_overlay()
    except FileNotFoundError as e:
        print(e)
        talk("Could not load the Iron Man image. Please check the file path.")
        return None

    while True:
        ret, frame = cap.read()
        if ret:
            frame = overlay_iron_man_face(frame, iron_man_overlay)
            cv2.imshow('Jarvis with Iron Man Overlay', frame)
            if cv2.waitKey(1) == ord('q'):
                break

        with sr.Microphone() as source:
            print("Listening...")
            voice = listener.listen(source)
            try:
                command = listener.recognize_google(voice)
                command = command.lower()  
                print(f"Recognized command: {command}")  
                if 'jarvis' in command:  # Check if 'jarvis' is present
                    command = command.replace('jarvis', '')  # Remove 'jarvis' if found
                return command
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return None

def send_whatsapp_message(phone_number, message):
    """Sends a WhatsApp message to the given phone number with the specified message."""
    try:
        pywhatkit.sendwhatmsg_instantly(phone_number, message)  
        talk("Message sent successfully.")
    except Exception as e:
        print(f"An error occurred while sending the message: {e}")
        talk("There was an error sending the message. Please try again.")

def perform_calculation(command):
    """Performs basic mathematical calculations."""
    try:
        
        command = command.replace('calculate', '').strip()
        print(f"Calculation command: {command}")  

        if 'plus' in command or '+' in command:
            if 'plus' in command:
                numbers = command.split('plus')
            else:
                numbers = command.split('+')
            result = float(numbers[0]) + float(numbers[1])
            print(result)
        elif 'minus' in command or '-' in command:
            if 'minus' in command:
                numbers = command.split('minus')
            else:
                numbers = command.split('-')
            result = float(numbers[0]) - float(numbers[1])
            print(result)
        elif 'times' in command or '*' in command:
            if 'times' in command:
                numbers = command.split('times')
            else:
                numbers = command.split('*')
            result = float(numbers[0]) * float(numbers[1])
            print(result)
        elif 'divided by' in command or '/' in command:
            if 'divided by' in command:
                numbers = command.split('divided by')
            else:
                numbers = command.split('/')
            result = float(numbers[0]) / float(numbers[1])
            print(result)
        else:
            talk("I couldn't understand the calculation. Please try again.")
            return

        talk(f"The result is {result}")
    except Exception as e:
        print(f"An error occurred during the calculation: {e}")
        talk("There was an error performing the calculation. Please try again.")

def run_jarvis():
    while True:
        command = get_command()
        if command:
            print(f"Processing command: {command}")  
            if 'how are you' in command:
                talk("I am doing well, how can I assist you today?")
                break
            elif 'what is your name' in command:
                talk("I am Jarvis, your personal assistant.")
                break
            elif 'who is' in command:
                person = command.replace('who is', '')
                info = wikipedia.summary(person, sentences=2)  
                print(info)
                talk(info)
                break
            elif 'time' in command:
                now = datetime.datetime.now().strftime('%I:%M %p')  
                print(now)
                talk('Current time is ' + now)
                break
            elif 'date' in command:
                today = datetime.date.today().strftime('%d / %m / %Y')
                print(today)
                talk("Today's date is " + today)
                break
            elif 'play' in command:
                song = command.replace('play', '')
                talk("Playing " + song)
                pywhatkit.playonyt(song)
                break
            elif 'send whatsapp message' in command:
                
                try:
                    parts = command.split('to')
                    phone_number = parts[1].split('message')[0].strip()  # Assuming phone number comes after 'to'
                    message = parts[1].split('message')[1].strip()  # Assuming message comes after 'message'
                    send_whatsapp_message(phone_number, message)
                except IndexError:
                    talk("I couldn't understand the phone number or message. Please try again, specifying 'to' and 'message'.")
            elif 'calculate' in command:
                perform_calculation(command)
                break
            else:
                talk("I can't help you with that yet, but I'm still learning.")

if __name__ == "__main__":
    run_jarvis()
