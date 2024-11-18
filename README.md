# Assistant Bot

Assistant Bot is a Python-based desktop virtual assistant developed using PyQt5, which can handle text and voice commands. It responds with text and optionally with speech. The bot can process a variety of commands and can be shut down gracefully upon request.

## Features

- **Text Command Input**: Users can type their commands directly.
- **Voice Command Input**: Users can issue commands via voice recognition.
- **Voice Responses**: The assistant can provide responses using text-to-speech.
- **Shutdown Command**: The bot can be closed with a "shutdown" command while providing a spoken farewell message.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Omrohit04/assistant-bot.git
    cd assistant-bot
    ```

2. **Install dependencies**:
    Ensure you have Python installed (Python 3.6 or higher recommended). Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

    **Create `requirements.txt` with**:
    ```text
    PyQt5
    pyaudio
    SpeechRecognition
    pyttsx3
    ```
    
3. **Run the application**:
    ```bash
    python AssistantBot.py
    ```

## How to Use

1. Launch the bot by running `AssistantBot.py`.
2. Enter commands through the input box and press "Submit" or hit "Enter".
3. Use the "Listen" button to give voice commands (make sure your microphone is enabled).
4. To enable or disable voice output, use the provided checkbox.
5. To shut down the bot, type or say "shutdown", and it will respond with a farewell before closing.

## Customization

- **Add More Commands**: Extend the `handle_query()` function with custom command responses.
- **Modify Voice Settings**: Adjust the `speak()` function for different voices or speeds.

## Contributing

Contributions are encouraged! Feel free to fork this repository, make enhancements, and submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- **PyQt5** for the graphical interface.
- **SpeechRecognition** and **pyaudio** for voice input functionality.
- **pyttsx3** for text-to-speech capabilities.
