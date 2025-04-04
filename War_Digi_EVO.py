# === Función para generar canciones ===
# Convenciones de nombres
#   Song    ->   Sound, music, etc
#   Lyric   ->   Text of the song
#   Desc    ->   Description
#   Name    ->   Prompt from the user

# Flujo de la aplicación:
# - De Name -> Desc
# - De Desc -> LDesc
# - De LDesc -> Lyric
# - De Lyric -> Title
# - De Lyric -> Style
# - De Lyric -> Song
# - Genera archivo JSON con Name, Language, Desc, Song y carpeta con MP3

import json
import torch
import tensorflow as tf
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget
from transformers import pipeline

# ---------------- Constants ----------------
SUPPORTED_LANGUAGES = [  # A list of supported languages for the application
    "English", "Mandarin Chinese", "Spanish", "Hindi", "Arabic",
    "French", "Bengali", "Portuguese", "Russian", "Japanese"
]

# Constantes para prompts comunes
TITLE_PROMPT_TEMPLATE = (
    "Actúa como un especialista en producción musical y branding. Considera la siguiente descripción de un álbum: "
    "'{description}'. Produce una lista de 5 opciones creativas y únicas que podrían ser utilizadas como título "
    "del álbum. Las opciones deben ser únicas, inspiradoras y provocar curiosidad."
    "\n\nEjemplo de salida:\n"
    "1. El Renacimiento del Fénix\n"
    "2. Ecos de la Eternidad\n"
    "3. Fragmentos de un Sueño\n"
)

COVER_PROMPT_TEMPLATE = (
    "Eres un ilustrador y diseñador gráfico especializado en portadas de álbumes. Basándote en esta descripción del álbum: "
    "'{description}', genera 5 prompts detallados diseñados para modelos txt2img. Los prompts deben enfocarse en "
    "colores, temas visuales, emociones, texturas y estilos artísticos específicos para garantizar resultados impresionantes."
    "\n\nEjemplo de salida:\n"
    "- Un paisaje surrealista al anochecer con tonos púrpuras y dorados, un fénix renaciendo de las cenizas al fondo.\n"
    "- Un mundo abstracto inspirado en el arte impresionista con colores vibrantes y formas fluidas."
)

# Constantes para prompts comunes

TITLE_PROMPT_TEMPLATE = (
    "Actúa como un especialista en producción musical y branding. Considera la siguiente descripción de un álbum: "
    "'{description}'. Produce una lista de 5 opciones creativas y únicas que podrían ser utilizadas como título "
    "del álbum. Las opciones deben ser únicas, inspiradoras y provocar curiosidad."
    "\n\nEjemplo de salida:\n"
    "1. El Renacimiento del Fénix\n"
    "2. Ecos de la Eternidad\n"
    "3. Fragmentos de un Sueño\n"
)

WINDOW_TITLE = "Digimon Song Generator"  # Introducción de constante


# === Clase Lyrica ===

class Lyric:
    EMPTY_STRING = ""

    def __init__(self, text: str, singer: str, is_based_on: bool,
                 name: str = EMPTY_STRING, style: str = EMPTY_STRING,
                 song_filename: str = EMPTY_STRING):
        self.text = text
        self.singer = singer
        self.is_based_on = is_based_on
        self.name = name
        self.style = style
        self.song_filename = song_filename
        self.song_handle = self.EMPTY_STRING

# === Clase Album ===

class Album:
    AI_MODEL_NAME = "EleutherAI/gpt-neo-2.7B"
    JSON_FILE_PATH = "digimon_albums.json"
    def __init__(self, name):
        self.name = name
        self.content = []  # Lista de letras de canciones
        self.description = None  # Descripción general del álbum
        self.cover_options = []  # Opciones generadas para la portada
        self.title_options = []  # Opciones generadas para el título
    def generate_album_titles(self):
        """
        Genera 5 títulos creativos para el álbum basado en su descripción.
        """
        if not self._validate_description():
            return []

        prompt = TITLE_PROMPT_TEMPLATE.format(description=self.description)
        self.title_options = self._generate_ai_responses(prompt, max_length=150)[:5]
        return self.title_options
    def generate_cover_prompts(self):
        """
        Genera 5 prompts detallados para la creación de portadas utilizando modelos txt2img.
        """
        if not self._validate_description():
            return ["Descripción vacía."]

        prompt = COVER_PROMPT_TEMPLATE.format(description=self.description)
        self.cover_options = self._generate_ai_responses(prompt, max_length=350)[:5]
        return self.cover_options
    def generate_description(self):
        """
        Genera una descripción inspiradora y rica basada en las canciones incluidas en el álbum.
        """
        if not self.content:
            self.description = "El álbum no contiene canciones."
            return self.description

        formatted_songs = "\n".join([f"- {song}" for song in self.content])
        prompt = (
            f"Eres un crítico musical renombrado y escritor creativo. Imagina que estás escribiendo una descripción apasionante para un álbum "
            f"titulado '{self.name}'. Este álbum contiene las siguientes canciones:\n"
            f"{formatted_songs}\n\n"
            "Escribe una descripción rica y evocadora que capte la esencia del álbum, sus emociones y su narrativa. Usa un lenguaje poético, "
            "apasionado y altamente descriptivo. Evita usar lenguaje genérico o referencias a propiedades protegidas como nombres de franquicias."
            "\n\nEjemplo de descripción:\n"
            "Este álbum transporta al oyente a un viaje emocional a través del tiempo, explorando temas de resiliencia, renacimiento y nostalgia. "
            "Cada canción entreteje una narrativa íntima que resuena profundamente en el alma."
        )
        descriptions = self._generate_ai_responses(prompt, max_length=300)
        self.description = descriptions[0] if descriptions else "Descripción no generada."
        return self.description
    def _validate_description(self):
        """
        Valida que la descripción esté presente.
        """
        if not self.description:
            print("Descripción ausente. No se puede proceder.")
            return False
        return True
    def _generate_ai_responses(self, prompt, max_length=50, num_return_sequences=1):
        """
        Función auxiliar para interactuar con el modelo AI y devolver respuestas procesadas.
        """
        try:
            text_generator = pipeline("text-generation", model=self.AI_MODEL_NAME)
            responses = text_generator(prompt, max_length=max_length, num_return_sequences=num_return_sequences)
            return [res["generated_text"].strip() for res in responses]
        except Exception as e:
            print(f"Error al generar respuesta con AI: {e}")
            return []

# === Clase Digimon ===

class Digimon:
                AI_MODEL_NAME = "EleutherAI/gpt-neo-125M"  # Constante para el modelo
                EVOLUTION_PROMPT_TEMPLATE = (
                    "Generate a detailed and plausible evolutionary progression for the "
                    "Digimon '{name}'. Include all stages from Rookie to Mega."
                )
                DESCRIPTION_PROMPT_TEMPLATE = (
                    "You are a creative storyteller, writing vivid descriptions for fictional creatures. "
                    "Describe the Digimon '{name}' in detail, including:\n"
                    "- Its physical appearance and unique traits.\n"
                    "- Its personality and behavior.\n"
                    "- The special powers and abilities it possesses.\n"
                    "Write in an engaging and inspiring tone suitable for fans of fantasy stories."
                )

                def __init__(self, name):
                    """Inicializa el objeto Digimon con su nombre, lista de evoluciones y descripciones."""
                    self.name = name
                    self.evolution_list = self._generate_evolutions()
                    self.descriptions = self._generate_stage_descriptions()
                    self.lyrics = {}

                def _create_text_generator(self):
                    """Inicializa y devuelve un generador de texto."""
                    from transformers import pipeline
                    try:
                        return pipeline("text-generation", model=self.AI_MODEL_NAME)
                    except Exception as e:
                        print(f"Error initializing text generator: {e}")
                        return None

                def _generate_ai_text_responses(self, prompt, max_length=100, num_return_sequences=1):
                    """Genera texto utilizando el modelo AI."""
                    generator = self._create_text_generator()
                    if not generator:
                        return None  # Evita lanzar excepciones si el modelo no se inicializa
                    try:
                        response = generator(prompt, max_length=max_length, num_return_sequences=num_return_sequences)
                        return response
                    except Exception as e:
                        print(f"Error generating AI response: {e}")
                        return None

                def _generate_evolutions(self):
                    """Genera la lista de evoluciones para el Digimon basado en IA."""
                    prompt = self.EVOLUTION_PROMPT_TEMPLATE.format(name=self.name)
                    ai_response = self._generate_ai_text_responses(prompt, max_length=100, num_return_sequences=1)
                    if not ai_response:
                        return []  # Retornar vacío si no se pudo generar respuesta
                    return [stage.strip() for stage in ai_response[0]["generated_text"].split(",") if stage.strip()]

                def _generate_stage_descriptions(self):
                    """Genera descripciones para cada etapa de evolución del Digimon."""
                    descriptions = {}
                    for digimon_name in self.evolution_list:
                        descriptions[digimon_name] = self._generate_description(digimon_name)
                    return descriptions

                def _generate_description(self, digimon_name):
                    """Genera la descripción para un único nombre de Digimon."""
                    prompt = self.DESCRIPTION_PROMPT_TEMPLATE.format(name=digimon_name)
                    ai_response = self._generate_ai_text_responses(prompt, max_length=250, num_return_sequences=1)
                    if not ai_response:
                        return "Description could not be generated."
                    return ai_response[0]["generated_text"].strip()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_main_window()

    def setup_main_window(self):  # Extracción de setup para simplificar __init__
        """Configura la ventana principal y sus elementos."""
        self.setWindowTitle("Ejemplo PyQt5")
        self.setGeometry(100, 100, 400, 300)

        # Crear widgets
        self.label = QLabel("¡Hola, PyQt5!", self)
        self.line_edit = QLineEdit(self)
        self.button = QPushButton("Presionar", self)
        self.button.clicked.connect(self.on_button_click)  # Conexión de evento

        # Configurar layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

        # Configuración del contenedor principal
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_button_click(self):
        """Actualiza el texto del label según la entrada del usuario."""
        text = self.line_edit.text()
        self.label.setText(f"Hola, {text}!")

class DigimonApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz gráfica de usuario."""
        layout = QVBoxLayout()

        self.instruction_label = QLabel("Enter Digimon names separated by commas:")
        layout.addWidget(self.instruction_label)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        self.generate_button = QPushButton("Generate Songs")
        self.generate_button.clicked.connect(self.generate_songs)
        layout.addWidget(self.generate_button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def generate_songs(self):
        """Genera canciones basadas en los nombres de los Digimon ingresados."""
        digimon_names = self.get_valid_digimon_names(self.input_field.text())

        if not digimon_names:
            self.result_label.setText("No valid names were provided.")
        else:
            # Aquí podría ir la lógica de generación
            # Por ejemplo:
            # results = generate_digimon_songs(digimon_names)
            # save_results_to_file(results)
            self.result_label.setText("Songs and descriptions generated and saved!")

    @staticmethod
    def get_valid_digimon_names(input_text):
        """Procesa los nombres de Digimon ingresados y devuelve una lista limpia."""
        return [name.strip() for name in input_text.split(",") if name.strip()]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
