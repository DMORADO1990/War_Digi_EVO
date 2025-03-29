from transformers import pipeline
import json
from tqdm import tqdm  # Para mostrar progreso visual durante la generación
from tkinter import Tk, Label, Entry, Button

from transformers import pipeline

#Ejemplo/Test
text_generator = pipeline("text-generation", model="EleutherAI/gpt-neo-2.7B")
response = text_generator("Escribe una descripción creativa sobre un Digimon llamado Greymon:", max_length=50)
print(response)

# === Función para generar canciones ===
def generate_song_text(digimon_name, model_name="EleutherAI/gpt-neo-2.7B"):
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
    - Gran energia, espiritu y sentimiento de forma que el resultado sea de exepcional calidad.
    Elige un estilo basado en la letra y ademas escoge un tiltulo acorde para la misma.
    """
    try:
        response = text_generator(prompt, max_length=3000, num_return_sequences=1)
        return response[0]["generated_text"].strip()
    except Exception as e:
        print(f"Error generando canción para {digimon_name}: {e}")
        return "Error al generar canción."


# === Función para generar audio basado en texto ===
def generate_audio_from_text(song_text, audio_file_name, model_name="suno/bark-small"):
    """
    Convierte el texto de la canción en audio utilizando un modelo text-to-speech.
    """
    text_to_speech = pipeline("text-to-speech", model=model_name)
    try:
        result = text_to_speech(song_text)
        with open(audio_file_name, "wb") as f:
            f.write(result["audio"])
        print(f"Archivo de audio guardado como {audio_file_name}")
        return audio_file_name.mp4
    except Exception as e:
        print(f"Error generando audio: {e}")
        return None


# === Función para traducir texto a otro idioma ===
def translate_text(text, target_language="es", model_name="Helsinki-NLP/opus-mt-en-es"):
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


# === Función principal para procesar canciones y audios por Digimon ===
def generate_digimon_songs(digimon_list):
    """
    Genera tres versiones de canciones por cada Digimon: original, voz del Digimon, voz del Tamer.
    """
    songs = {}
    for digimon_name in tqdm(digimon_list, desc="Generando canciones"):
        original_song = generate_song_text(digimon_name)
        digimon_voice_song = generate_audio_from_text(original_song, f"{digimon_name}_digimon_voice.wav")
        tamer_voice_song = generate_audio_from_text(original_song, f"{digimon_name}_tamer_voice.wav")

        songs[digimon_name] = {
            "original_song_text": original_song,
            "digimon_voice_audio": digimon_voice_song,
            "tamer_voice_audio": tamer_voice_song
        }
    return songs


# === Función para guardar resultados en un archivo JSON ===
def save_results_to_file(data, filename="digimon_songs.json"):
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


# === Punto de entrada principal ===
if __name__ == "__main__":
    print("Modo de uso"
          "1-In Terminal"
          "2-On GUI"
          "")
    mode = input("Selecciona: ").strip().lower()

    if mode == "2":
        gui()
    else:
        print("Bienvenido")
        input_names = input("Ingrese el nombres de Digimon seleccionado: ").split(",")
        input_names = [name.strip() for name in input_names if name.strip()]

        if not input_names:
            print("No se proporcionaron nombres válidos.")
        else:
            print("\nProcesando, esto puede tomar unos momentos...\n")
            results = generate_digimon_songs(input_names)
            save_results_to_file(results)

            print("\nCanciones Generadas:\n")
            for digimon_name, data in results.items():
                print(f"{digimon_name}:\nTexto Original:\n{data['original_song_text']}\n")
                print(f"Archivo de Voz Digimon: {data['digimon_voice_audio']}")
                print(f"Archivo de Voz Tamer: {data['tamer_voice_audio']}\n")
