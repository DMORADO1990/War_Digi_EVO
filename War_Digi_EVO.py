import json
from tkinter import Tk, Label, Entry, Button
from tqdm import tqdm  # Para mostrar progreso visual durante la generación
from transformers import pipeline

# Ejemplo/Test
text_generator = pipeline("text-generation", model="EleutherAI/gpt-neo-2.7B")
response = text_generator("Escribe una descripción creativa sobre un Digimon llamado Greymon:", max_length=50)
print(response)


# === Función para generar canciones ===
# Name convention
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

# === Clase Album ===
class Album:
    def __init__(self, name):
        self.name = name
        self.desc = ""
        self.lyrics = []
        self.cover = None

    def createdescfromlyrics(self):
        """
        Genera una descripción del álbum basado en su contenido.
        """
        if not self.lyrics:
            return "El álbum no contiene canciones."
        self.desc = f"Eres un experto en produccion musical proporciona una descripcion basada en '{self.lyrics}' de un album musical basados en las siguientes canciones '{len(album.lyrics)}' asegura que sea apasionada y emocionante que te enganche de inmediato y que tenga menos de 300ch. Puedes ser altamante poetico y artistico. Asegura no utilizar ningun lenguaje propietario de la franquisia"
        return desc

    def createnamefromdesc(self):
        """
        Crea un titulo para el álbum basado en su descripcion.
        """
        if not self.lyrics:
            return "El álbum no contiene canciones."
        self.name = f"Eres un experto en produccion musical proporciona al menos 5 opciones para el titulo de un album basado en '{self.lyrics}' asegura no utilizar ningun lenguaje propietario de la franquisia' "
        return desc

    def createcoverfromdesc(self):
        """
        Crea una portada para el álbum basado en su descripcion.
        """
        self.cover = f"Eres un experto en prompts crea un prompt pata la portada de un album de que represente la '{album.name}' con canciones.'{self.lyrics}'"
        return self.cover  # Todo change prompt

    def addlyricstoalbum(self, lyrics):
        """
        Añade las letras de canciones al álbum.
        """
        self.lyrics.append(lyrics)


# === Clase Digimon ===
class Digimon:
    def __init__(self, name):
        self.name = name
        self.evol_list = []
        self.descriptions = []
        self.lyrics = []
        self.translated_descriptions = []

        def generatedescfromname(digimon_name, model_name="EleutherAI/gpt-neo-2.7B"):
            """
            Genera una descripción creativa basada en el nombre del Digimon utilizando un modelo AI.
            """
            text_generator = pipeline("text-generation", model=model_name)
            prompt = f"""
            Eres un experto escritor y artista. Describe al Digimon llamado {self.name} de manera única. Asegura no usar 
            La descripción debe incluir:
            - Las habilidades principales del Digimon.
            - Su personalidad distintiva.
            - Su entorno natural o lugar donde habita.
            - Sus fortalezas y debilidades.
            - Un toque épico que inspire admiración.
            """
            try:
                response = text_generator(prompt, max_length=500, num_return_sequences=1)
                description = response[0]["generated_text"].strip()
                return description
            except Exception as e:
                print(f"Error generando descripción para {digimon_name}: {e}")
                return f"No se pudo generar la descripción para {digimon_name}."

    def translate_desc(text, target_language="es", model_name="Helsinki-NLP/opus-mt-en-es"):
        """
        Traduce texto a otro idioma usando Hugging Face.
        """
        translator = pipeline("translation", model=model_name)
        try:
            result = translator(text, max_length=300)
            return result[0]['translation_text']
        except Exception as e:
            print(f"Error traduciendo texto: {e}")
            return "Error al traducir texto."

    def generate_lyric_from_desc(digimon_name, model_name="EleutherAI/gpt-neo-2.7B"):
        """
        Genera el texto de una canción original basada en el Digimon usando un modelo seleccionado.
        """
        text_generator = pipeline("text-generation", model=model_name)
        prompt = f"""
        Eres un compositor profesional y creativo. Crea una canción inspirada en el digimon {digimon_name}.
        La canción debe incluir:
        - Tags para [] marcar distintas secciones.    
        - Rimas sofisticadas y métricas musicales refinadas.
        - Un tema que describa emocionalmente la personalidad, habilidades y hábitat del digimon.
        - Gran energía, espíritu y sentimiento de forma que el resultado sea de excepcional calidad.
        Elige un estilo basado en la letra y además escoge un título acorde para la misma.
        """
        try:
            response = text_generator(prompt, max_length=3000, num_return_sequences=1)
            return response[0]["generated_text"].strip()
        except Exception as e:
            print(f"Error generando canción para {digimon_name}: {e}")
            return "Error al generar canción."

    def generate_song_from_lyrics(song_text, audio_file_name, model_name="suno/bark-small"):
        """
        Convierte el texto de la canción en audio utilizando un modelo text-to-speech.
        """
        text_to_speech = pipeline("text-to-speech", model=model_name)
        try:
            result = text_to_speech(song_text)
            with open(audio_file_name, "wb") as f:
                f.write(result["audio"])
            print(f"Archivo de audio guardado como {audio_file_name}")
            return audio_file_name
        except Exception as e:
            print(f"Error generando audio: {e}")
            return None

    def save_to_json(data, filename="digimon_songs.json"):
        """
        Guarda las canciones generadas en un archivo JSON.
        """
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"\nCanciones guardadas exitosamente en el archivo {filename}.")
        except Exception as e:
            print(f"Error al guardar los resultados: {e}")


# === Interfaz Gráfica (Tkinter) ===
def gui():
    """
    Crear una GUI básica para introducir nombres de Digimon y generar resultados.
    """
    window = Tk()
    window.title("Generador de Canciones y Descripciones de Digimon")
    Label(window, text="Ingrese los nombres de los Digimon separados por comas:").pack()
    input_field = Entry(window, width=50)
    input_field.pack()

    def generate():
        names = input_field.get().split(",")
        names = [name.strip() for name in names if name.strip()]
        if not names:
            Label(window, text="No se proporcionaron nombres válidos.").pack()
        else:
            results = generate_digimon_songs(names)
            save_results_to_file(results)
            Label(window, text="¡Canciones y descripciones generadas y guardadas!").pack()

    Button(window, text="Generar Canciones", command=generate).pack()
    window.mainloop()


# Example of how to use the class
if __name__ == "__main__":
    digimon_name = input("Enter the Digimon's name: ")
    digimon = Digimon(digimon_name)

    digimon.GenerateEvolListfromName()
    digimon.GenerateDescfromName()
    digimon.GenerateLyricfromDesc()
    digimon.TranslateDesc()

    print("\nEvolution List:")
    print(digimon.evol_list)
    print("\nDescriptions:")
    print(digimon.descriptions)
    print("\nLyrics:")
    print(digimon.lyrics)
    print("\nTranslated Descriptions:")
    print(digimon.translated_descriptions)

# === Ejecución del programa ===
if __name__ == "__main__":
    gui()
