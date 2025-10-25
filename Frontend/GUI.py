import os
import sys

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QStackedWidget
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import load_dotenv, dotenv_values
from Backend.EmergencyDetector import start_detection, stop_recording
from Frontend.EmergencyButton import EmergencyButton

# Load environment variables from .env file
load_dotenv()
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chats_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's","where's","how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r",encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w",encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r",encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path

def TempDirectoryPath(Filename):
    Path = rf'{TempDirPath}\{Filename}'
    return Path

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.txt', "w", encoding='utf-8') as file:
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Chat Text Display
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                color: white;
                border: 1px solid #333;
                padding: 15px;
                font-size: 28px;
                border-radius: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.5;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        layout.addWidget(self.chat_text_edit)

        # Input Section
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)
        
        # Voice Input Button
        self.voice_button = QPushButton()
        self.voice_button.setIcon(QIcon(GraphicsDirectoryPath('mic.png')))
        self.voice_button.setIconSize(QSize(40, 40))
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #333;
                padding: 10px;
                font-size: 20px;
                border-radius: 10px;
                min-width: 70px;
                max-width: 70px;
                min-height: 70px;
                max-height: 70px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        """)
        self.voice_button.clicked.connect(self.toggle_voice_input)
        input_layout.addWidget(self.voice_button)
        
        # Text Input
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(70)
        self.text_input.setPlaceholderText("Type your message here...")
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #333;
                padding: 15px;
                font-size: 20px;
                border-radius: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit::placeholder {
                color: #888;
            }
        """)
        input_layout.addWidget(self.text_input)
        
        # Send Button
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #333;
                padding: 10px;
                font-size: 20px;
                border-radius: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 70px;
                min-height: 70px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Status Label
        self.label = QLabel("Available...")
        self.label.setStyleSheet("""
            color: #888;
            font-size: 27px;
            border: none;
            margin-top: 15px;
            font-weight: medium;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Set Timer for Updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateUI)
        self.timer.start(100)

        # Voice input state
        self.is_listening = False
        self.last_message = ""

        # Set Overall Layout Style
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def toggle_voice_input(self):
        """Toggle voice input on/off."""
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.voice_button.setIcon(QIcon(GraphicsDirectoryPath('mic_on.png')))
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 25px;
                    border-radius: 5px;
                    min-width: 50px;
                    max-width: 50px;
                }
                QPushButton:hover {
                    background-color: #cc0000;
                }
                QPushButton:pressed {
                    background-color: #990000;
                }
            """)
            SetMicrophoneStatus("True")
            self.label.setText("Listening...")
        else:
            self.voice_button.setIcon(QIcon(GraphicsDirectoryPath('mic.png')))
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 25px;
                    border-radius: 5px;
                    min-width: 50px;
                    max-width: 50px;
                }
                QPushButton:hover {
                    background-color: #005999;
                }
                QPushButton:pressed {
                    background-color: #004d80;
                }
            """)
            SetMicrophoneStatus("False")
            self.label.setText("Available...")

    def send_message(self):
        """Send the message from the text input."""
        message = self.text_input.toPlainText().strip()
        if message:
            # Add message to chat
            self.addMessage(f"{Username}: {message}", 'white')
            
            # Clear input
            self.text_input.clear()
            
            # Add to query queue
            from Main import query_queue
            query_queue.put(message)

    def updateUI(self):
        """Update both messages and status."""
        try:
            # Update messages
            with open(TempDirectoryPath('Responses.txt'), "r", encoding='utf-8') as file:
                messages = file.read()
                if messages and messages != self.last_message:
                    self.addMessage(messages, 'white')
                    self.last_message = messages

            # Update status
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                status = file.read()
                if status and status != self.label.text():
                    self.label.setText(status)

            # Check for voice input
            if self.is_listening:
                with open(TempDirectoryPath('VoiceInput.txt'), "r", encoding='utf-8') as file:
                    voice_input = file.read().strip()
                    if voice_input:
                        self.text_input.setText(voice_input)
                        self.send_message()
                        # Clear the voice input file
                        with open(TempDirectoryPath('VoiceInput.txt'), "w", encoding='utf-8') as f:
                            f.write("")

        except Exception as e:
            print(f"Error updating UI: {e}")

    def addMessage(self, message, color):
        """Add a message to the chat display."""
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        self.chat_text_edit.ensureCursorVisible()

    def loadMessages(self):
        global old_chats_message
        try:
            with open(TempDirectoryPath('Responses.txt'), "r", encoding='utf-8') as file:
                messages = file.read()

                if not messages:
                    pass
                elif len(messages) <= 1:
                    pass
                elif str(old_chats_message) == str(messages):
                    pass
                else:
                    self.addMessage(message=messages, color='white')
                    old_chats_message = messages
        except FileNotFoundError:
            with open(TempDirectoryPath('Responses.txt'), "w", encoding='utf-8') as file:
                file.write("")

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add GIF
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        
        # Add Emergency Button
        self.emergency_button = EmergencyButton()
        self.emergency_button.setFixedSize(200, 60)
        self.emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                padding: 15px;
                font-size: 20px;
                border-radius: 10px;
                min-width: 200px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        content_layout.addWidget(self.emergency_button, alignment=Qt.AlignCenter)
        
        # Add Mic Button
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.png'))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        
        # Add Status Label
        self.label = QLabel("")
        self.label.setStyleSheet("""
            color: white;
            font-size: 28px;
            margin-bottom: 0;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: #1e1e1e;")
        
        # Set Timer for Updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(500)

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: #1e1e1e;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.draggable = True  # Add draggable attribute
        self.offset = None     # Add offset attribute
        self.maximize_icon = QIcon(GraphicsDirectoryPath('maximize.png'))  # Add icons
        self.restore_icon = QIcon(GraphicsDirectoryPath('restore.png'))
        self.stacked_widget = stacked_widget
        self.initUI()
        self.current_screen = None

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # Title and Navigation
        title_section = QHBoxLayout()
        title_label = QLabel("Jarvis AI")
        title_label.setStyleSheet("""
            color: white;
            font-size: 25px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding-left: 10px;
        """)
        title_section.addWidget(title_label)
        
        # Navigation Buttons
        nav_buttons = QHBoxLayout()
        nav_buttons.setSpacing(20)  # Increased spacing between buttons
        
        # Home Button
        home_button = QPushButton()
        home_button.setIcon(QIcon(GraphicsDirectoryPath('home.png')))
        home_button.setIconSize(QSize(28, 28))  # Increased icon size
        home_button.setText("Home")
        home_button.setFixedSize(150, 45)  # Increased button size
        
        # Chat Button
        chat_button = QPushButton()
        chat_button.setIcon(QIcon(GraphicsDirectoryPath('chat.png')))
        chat_button.setIconSize(QSize(28, 28))  # Increased icon size
        chat_button.setText("Chat")
        chat_button.setFixedSize(150, 45)  # Increased button size
        
        # Common style for navigation buttons
        nav_button_style = """
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: none;
                padding: 8px 20px;
                font-size: 20px;  /* Increased font size */
                font-weight: bold;  /* Added bold text */
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 10px;  /* Increased border radius */
                text-align: left;
                padding-left: 20px;
                letter-spacing: 0.5px;  /* Added letter spacing */
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;  /* Added border on hover */
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
                border: 1px solid #005999;  /* Darker border when pressed */
            }
            QPushButton:checked {
                background-color: #007acc;
                border: 1px solid #005999;
            }
        """
        
        home_button.setStyleSheet(nav_button_style)
        chat_button.setStyleSheet(nav_button_style)
        
        nav_buttons.addWidget(home_button)
        nav_buttons.addWidget(chat_button)
        
        # Window Controls
        window_controls = QHBoxLayout()
        minimize_button = QPushButton("−")
        maximize_button = QPushButton("□")
        close_button = QPushButton("×")
        
        # Set fixed size for window control buttons
        for button in [minimize_button, maximize_button, close_button]:
            button.setFixedSize(45, 45)
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    font-size: 30px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    border-radius: 5px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #333;
                }
                QPushButton:pressed {
                    background-color: #444;
                }
            """)
            window_controls.addWidget(button)
        
        # Special styling for close button
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 30px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
            QPushButton:pressed {
                background-color: #f1707a;
            }
        """)
        
        # Connect buttons
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        chat_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        minimize_button.clicked.connect(self.minimizeWindow)
        maximize_button.clicked.connect(self.maximizeWindow)
        close_button.clicked.connect(self.closeWindow)
        
        # Add all sections to main layout
        layout.addLayout(title_section)
        layout.addStretch()
        layout.addLayout(nav_buttons)
        layout.addStretch()
        layout.addLayout(window_controls)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset is not None:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def mouseReleaseEvent(self, event):
        self.offset = None

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: #1e1e1e;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()