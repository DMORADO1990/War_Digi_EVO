import sys
import json
from tqdm import tqdm  # Para mostrar progreso visual durante la generación
from transformers import pipeline
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

# === Función para generar canciones ===
# Name convention
#   Song    ->   Sound, music, etc
#   Song    ->   Sound, music, etc
#   Lyric   ->   text of song
#   Desc    ->   descripted
#   Name    ->   Prompt from user

# App flow
# From Name->Desc
# From Desc->LDesc
# From LDesc->Lyric
# From Lyric->Title
# From Lyric->Style
# From Lyric->Song
# Docs out JSON Name, Language, Desc, Song, Folder with mp3

# === Clase Lyrica ===
class Lyric:
    def __init__(self, text, based, singer, name, style, song_filename):
        self.text = text
        self.based = based
        self.singer = singer
        self.name = ""
        self.style = ""
        self.song_filename = ""
        self.song_handdle = ""

# === Clase Digimon ===

class Digimon:
    def __init__(self, name):
        #Inicializa objeto empezando por nombre Digi.
        self.name = name
        self.evol_list = self.generate_evo_list()
        self.descriptions = self.generate_desc_for_each_name()
        self.lyrics = self.generate_song_from_lyrics()

    def generate_evo_list(self):
        """
        Generate a plausible and AI-generated evolution line for a given Digimon name.

        Parameters:
        digimon_name (str): The name of the Digimon.

        Returns:
        list: A list representing an AI-generated evolution line for the Digimon.
        """
        model_name = "Helsinki-NLP/opus-mt-en-es"
        # Pre-trained text generation model for AI (simulating this step with a mock)
        text_generator = pipeline("text-generation", model=model_name)

        # Prompt to guide AI generation
        prompt = "Generate the complete evolution line for the Digimon {name}."

        # AI generates response
        ai_response = text_generator(prompt, max_length=100, num_return_sequences=1)
        evolution_text = ai_response[0]["generated_text"]

        # Parse the response into a list of evolution stages (simple splitting for this example)
        evolution_line = [stage.strip() for stage in evolution_text.split(",")]

        return evolution_line

    def generate_desc_for_each_name(self):
        """
        Generate creative AI-generated descriptions for a list of Digimon names.

        Parameters:
        digimon_list (list): A list of Digimon names.

        Returns:
        dict: A dictionary with each Digimon name as the key and its description as the value.
        """
        model_name = "gpt-2"
        try:
            # Pre-trained text generation model for AI
            text_generator = pipeline("text-generation", model=model_name)  # Example: GPT-2 model

            # Dictionary to store results
            descriptions = {}
            translations = {}
            prominent_languages = [
                "English",
                "Mandarin Chinese",
                "Spanish",
                "Hindi",
                "Arabic",
                "French",
                "Bengali",
                "Portuguese",
                "Russian",
                "Japanese"
            ]
            # Loop through the list of Digimon names
            for name in self.evol_list:
                for language in prominent_languages:
                    # Prompt for generating the description
                    prompt = """
                    You are a professional and creative composer. Create a description inspired by the Digimon {name}.
                    The description include:
                    - A catchy title.
                    - Tags to [mark different sections].
                    - Sophisticated rhymes and refined musical metrics.
                    - A theme that emotionally describes the personality, skills, and habitat of the Digimon.
                    - Great energy, spirit, and feeling, resulting in exceptional quality.
                    """.format(name=name)




# AI generates response
                    ai_response = text_generator(prompt, max_length=3000, num_return_sequences=1)
                    description = ai_response[0]["generated_text"].strip()
                    translations[language] = description
                # Add the description to the dictionary
                descriptions[name] = translations
            return descriptions

        except Exception as e:
            print(f"Error generating descriptions: {e}")
            return {"Error": "Could not generate descriptions for the provided Digimon names."}

    def generate_lyrics_for_each_desc(self):
        """
        Recorre self.descriptions y genera un objeto de canción para cada Digimon, almacenándolo en self.lyrics.
        Cada canción incluye título, autor, estilo, letra, y un identificador único.
        """
        model_name = "gpt-2"
        try:
            lyrics = {} # Placeholder lyrics

            # Pre-trained text generation model for AI
            text_generator = pipeline("text-generation", model=model_name)
            for author in ["Observador External" ,"El Digimon" ,"El Tamer"]:
                # Loop through all descriptions in self.descriptions
                for name, language in self.descriptions.items():
                    # Prompt for generating the song
                    prompt = f"""
                    Eres un compositor profesional y creativo. Crea una canción inspirada en el Digimon {digimon_name}.
                    Basándote en la descripción: {self.descriptions[name, language]} ---
                    La canción debe incluir:
                    - La perspectiva de ser cantada por {author}
                    - Tags para [marcar distintas secciones].
                    - Rimas sofisticadas y métricas musicales refinadas.
                    - Un tema que describa emocionalmente la personalidad, habilidades y hábitat del Digimon.
                    - Gran energía, espíritu y sentimiento de forma que el resultado sea de excepcional calidad.
                    - Puede ser una cancion cantada por el autor desde su perspectiva cultural o un relato de sus aventuras o cualquier otro
                    - Asegura que el estilo esta acorde con los top 10 exitos del mundo del ultimo ano
                    - La cancion misma deberia reflejar la madures amocional y intereses acordes a el nivel del digimon.
                        Ejem: para un digimon nivel BB se esperaria una cancion muy infantil, llena de inocencia. Mientras que la cancion de un Mega deberia sonar llena de sabiduria en un tomo mas ancestral donde se denote la experiencia y el poder 
                    No debera utilizar info propietarioa o con derecho de autor. Esto incluye el nombre del digimon mismo y sus tecnicas
                    Todo deberia ser muy subjetivo, emocional y elegante.
                    """
                    try:
                        # Generate song content
                        response = text_generator(prompt, max_length=500, num_return_sequences=1)
                        generated_text = response[0]["generated_text"].strip()
                        lyric_tx = generated_text

                        response = text_generator("provide a title for song {lyric_tx}", max_length=500, num_return_sequences=1)
                        generated_text = response[0]["generated_text"].strip()
                        title = generated_text

                        response = text_generator(f"""
                        provide a style for song {lyric_tx}, based on {digimon_name} and sang by singer {author} as
                        python coma separated list.
                        -Make sure the selected style match current lyric, 
                        -Make sure the selected style with one of 50 top songs on last 6 months
                        -Make sure not tu use any propietary info
                        -Always add: male singer, polished production, energetic, sentimental, epic chorus, emotional, great vocals
                        """,
                        max_length=500,
                        num_return_sequences=1)

                        generated_text = response[0]["generated_text"].strip()
                        style = generated_text


                        dir = f"{name.lower()}//{author.lower()}//{title.lower()}({style})"

                        # Create a song object and store it in self.lyrics
                        song_object = Lyric(lyric_tx, name, author, title, style, dir)
                        lyrics[name][language][author] = song_object

                    except Exception as inner_exception:
                        print(f"Error generando canción para {digimon_name}: {inner_exception}")
        except Exception as e:
            print(f"Error inicializando el modelo: {e}")

    def generate_song_from_lyrics(self) \
         -> None:"""

        #Convierte el texto de la canción en audio utilizando un modelo text-to-speech.

        model_name = "suno/bark-small"
        text_to_speech = pipeline("text-to-speech", model=model_name)
        try:
            result = text_to_speech(song_text)
            with open(audio_file_name, "wb") as f:
                f.write(result["audio"])
            print(f"Archivo de audio guardado como {audio_file_name}")
            return audio_file_name
        except Exception as e:
            print("Error generando audio: {e}")
            return None

    def save_to_json(data, filename="digimon_songs.json"):
       
        #Guarda las canciones generadas en un archivo JSON.
       
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print("\nCanciones guardadas exitosamente en el archivo {filename}.")
        except Exception as e:
            print(f"Error al guardar los resultados: {e}")
"""

# === Clase Album ===

class Album:
    def __init__(self, name):
        self.name = name
        self.desc = ""
        self.lyrics = []
        self.cover = None

    def createdescfromlyrics(self, model_name = "EleutherAI/gpt-neo-2.7B"):
        """
        Genera una descripción del álbum basada en su contenido utilizando un modelo AI.
        """
        if not self.lyrics:
            return "El álbum no contiene canciones."

        # Improved prompt for generating the album description
        prompt = """
        Eres un experto en producción musical y en escribir críticas apasionantes sobre música. Proporciona una descripción rica y emocionante
        para un álbum titulado '{self.name}', basado en las siguientes ideas: '{self.desc}'.
        Asegúrate de que no incluya lenguaje propietario de ninguna franquicia.
        """

        try:
            # Generate text using the AI model
            text_generator = pipeline("text-generation", model_name)
            response = text_generator(prompt, max_length=1000, num_return_sequences=1)
            generated_desc = response[0]["generated_text"].strip()

            # Assign the generated description to the album
            desc = generated_desc
            return desc

        except Exception as e:
            print(f"Error album descripción '{self.name}': {e}")

    def createnamefromdesc(self, model_name = "EleutherAI/gpt-neo-2.7B"):
        """
            Genera una lista de nombres para el álbum basada en su contenido utilizando un modelo AI.
        """
        prompt = """
        Eres un experto en producción musical. Proporciona al menos 5 opciones creativas para el título de un álbum basado en la descripción: '{self.desc}'.
        Asegúrate de no usar ningún lenguaje propietario de la franquicia.
        """

        try:
            # Generate text using the AI model
            text_generator = pipeline("text-generation", model=model_name)
            response = text_generator(prompt, max_length=50, num_return_sequences=1)
            generated_text = response[0]["generated_text"].strip()

            # Process the response into a list of names
            titles = [title.strip() for title in generated_text.split("\n") if title.strip()]
            return titles[:5]  # Return only the first 5 options
        except Exception as e:
            print("Error generando nombres para el álbum: {e}")
            return ["Error al generar nombres para el álbum."]

    def createcoverfromdesc(self, model_name="EleutherAI/gpt-neo-2.7B"):
        """
        Crea cinco opciones detalladas para la portada del álbum optimizadas para modelos txt2img, basadas en su descripción.
        """
        if not self.desc:
            return ["No se puede generar una portada porque la descripción del álbum está vacía."]

        # Enhanced prompt tailored for txt2img models
        prompt = """
        Eres un experto en diseño visual y creación de arte para portadas de álbumes. Basándote en la siguiente descripción: '{self.desc}', 
        proporciona cinco prompts detallados adecuados para modelos txt2img que generen imágenes:
        """

        try:
            # Generate text using the AI model
            text_generator = pipeline("text-generation", model=model_name)
            response = text_generator(prompt, max_length=1000, num_return_sequences=1)
            generated_prompts = response[0]["generated_text"].strip()

            # Process the AI response to extract five distinct cover prompts
            cover_prompts = [prompt.strip() for prompt in generated_prompts.split("\n") if prompt.strip()]
            return cover_prompts[:5]  # Return only the first 5 options
        except Exception as e:
            print("Error generando la portada '{self.name}': {e}")
            return ["Error al generar prompts"]

    def addlyricstoalbum(self ,lyrics):
        """
        Añade las letras de canciones al álbum.
        """
        self.lyrics.append(lyrics)
"""
# === Interfaz Gráfica (QMainWindow) ===
class DigimonApp(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Generador de Canciones y Descripciones de Digimon")
        self.initUI()
    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Ingrese los nombres de los Digimon separados por comas:")
        layout.addWidget(self.label)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        self.generate_button = QPushButton("Generar Canciones")
        self.generate_button.clicked.connect(self.generate)
        layout.addWidget(self.generate_button)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def generate(self):
        names = self.input_field.text().split(",")
        names = [name.strip() for name in names if name.strip()]
        if not names:
            self.result_label.setText("No se proporcionaron nombres válidos.")
        else:
            #results = generate_digimon_songs(names)
            #save_results_to_file(results)
            self.result_label.setText("¡Canciones y descripciones generadas y guardadas!")
"""
# Example of how to use the class
if __name__ == "__main__":
    digimon_name = input("Enter the Digimon's name: ")
    digimon = Digimon(digimon_name)

    print("\nEvolution List:")
    print(digimon.evol_list)
    print("\nDescriptions:")
    print(digimon.descriptions)
    print("\nLyrics:")
    print(digimon.lyrics)
