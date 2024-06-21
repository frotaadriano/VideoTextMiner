from dotenv import load_dotenv
import os
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
import time
from tqdm import tqdm
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
from typing import List

# Carrega variáveis do arquivo .env / Load variables from .env file
load_dotenv()
subscription_key = os.getenv('AZURE_SUBSCRIPTION_KEY')
service_region = os.getenv('AZURE_SERVICE_REGION')

# Configura o serviço de reconhecimento de fala da Azure / Configure Azure Speech Service
speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
speech_config.speech_recognition_language = "pt-BR"  # Define o idioma para português do Brasil / Set language to Brazilian Portuguese

app = FastAPI()

# Função para dividir o áudio em segmentos menores / Function to split audio into smaller segments
def split_audio(audio_file, segment_length_ms=60000):
    audio = AudioSegment.from_file(audio_file)
    segments = []
    for i in range(0, len(audio), segment_length_ms):
        segments.append(audio[i:i + segment_length_ms])
    return segments

# Função para reconhecer fala de um segmento de áudio / Function to recognize speech from an audio segment
def recognize_speech_from_segment(segment_file) -> List[str]:
    audio_input = speechsdk.AudioConfig(filename=segment_file)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    result_texts = []

    def recognized(evt):
        result_texts.append(evt.result.text)
        print(f'Recognized: {evt.result.text}')

    done = False

    def stop(evt):
        nonlocal done
        print('CLOSING on {}'.format(evt))
        done = True

    speech_recognizer.recognized.connect(recognized)
    speech_recognizer.session_stopped.connect(stop)
    speech_recognizer.canceled.connect(stop)

    speech_recognizer.start_continuous_recognition()

    while not done:
        time.sleep(0.1)

    return result_texts

# Função para extrair áudio de um vídeo e converter em texto / Function to extract audio from a video and convert to text
def extract_audio_and_recognize_text(video_file):
    # Verifica se o arquivo de vídeo existe / Check if video file exists
    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"No such file: '{video_file}'")

    # Extrai o áudio do arquivo de vídeo e salva como WAV / Extract audio from video file and save as WAV
    audio_file = "extracted_audio.wav"
    AudioSegment.from_file(video_file).export(audio_file, format="wav")

    # Divide o áudio em segmentos menores / Split the audio into smaller segments
    segments = split_audio(audio_file)

    recognized_text = []

    start_time = time.time()  # Define o início do tempo / Define the start time

    # Processa cada segmento individualmente / Process each segment individually
    for i, segment in enumerate(tqdm(segments, desc="Processing")):
        segment_file = f"temp_segment_{i}.wav"
        segment.export(segment_file, format="wav")
        segment_texts = recognize_speech_from_segment(segment_file)
        recognized_text.extend(segment_texts)

    total_time = time.time() - start_time
    print(f'Total Time: {total_time} seconds')

    # Salva o texto reconhecido em um arquivo .txt / Save the recognized text to a .txt file
    transcript_file = video_file.replace('.mp4', '.txt')
    print("Recognized Text: ", recognized_text)   
    print("Transcript File: ", transcript_file)
     
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(" ".join(recognized_text))
    
    return transcript_file

# Endpoint para upload e processamento de vídeos / Endpoint for uploading and processing videos
@app.post("/upload_video/")
async def upload_video(file: UploadFile = File(...)):
    video_path = f"uploaded_{file.filename}"
    
    # Salva o arquivo de vídeo enviado / Save the uploaded video file
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        transcript_file = extract_audio_and_recognize_text(video_path)
        return JSONResponse(content={"message": "Transcription completed", "transcript_file": transcript_file})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

# Método para chamar a OpenAI (RAG) / Method to call OpenAI (RAG)
def call_openai_for_rag(text):
    # Esta função está pronta para ser implementada com a chamada à OpenAI / This function is ready to be implemented with OpenAI call
    pass

