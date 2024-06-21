from dotenv import load_dotenv
import os
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
import time
from tqdm import tqdm
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil

# Carrega variáveis do arquivo .env / Load variables from .env file
load_dotenv()
subscription_key = os.getenv('AZURE_SUBSCRIPTION_KEY')
service_region = os.getenv('AZURE_SERVICE_REGION')

# Configura o serviço de reconhecimento de fala da Azure / Configure Azure Speech Service
speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)

app = FastAPI()

# Função para extrair áudio de um vídeo e converter em texto / Function to extract audio from a video and convert to text
def extract_audio_and_recognize_text(video_file):
    # Verifica se o arquivo de vídeo existe / Check if video file exists
    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"No such file: '{video_file}'")

    # Extrai o áudio do arquivo de vídeo e salva como WAV / Extract audio from video file and save as WAV
    audio_file = "extracted_audio.wav"
    AudioSegment.from_file(video_file).export(audio_file, format="wav")

    # Configura a entrada de áudio para o reconhecedor de fala / Configure audio input for speech recognizer
    audio_input = speechsdk.AudioConfig(filename=audio_file)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    recognized_text = []

    # Função chamada sempre que um segmento de áudio é reconhecido / Function called whenever a segment of audio is recognized
    def recognized(evt):
        recognized_text.append(evt.result.text)
        print(f'Recognized: {evt.result.text}')

    # Função chamada quando a sessão de reconhecimento é interrompida / Function called when recognition session is stopped
    def stop(evt):
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()

    # Conecta os eventos de reconhecimento às funções definidas acima / Connect recognition events to the functions defined above
    speech_recognizer.recognized.connect(recognized)
    speech_recognizer.session_stopped.connect(stop)
    speech_recognizer.canceled.connect(stop)

    # Inicia o reconhecimento contínuo / Start continuous recognition
    start_time = time.time()
    speech_recognizer.start_continuous_recognition()

    # Calcula a duração do áudio para a barra de progresso / Calculate audio duration for progress bar
    duration = AudioSegment.from_file(video_file).duration_seconds
    with tqdm(total=duration, desc="Processing") as pbar:
        # Atualiza a barra de progresso enquanto o reconhecimento continua / Update progress bar as recognition continues
        while speech_recognizer.properties.get_property(speechsdk.PropertyId.SpeechServiceConnection_Url):
            time.sleep(1)
            pbar.update(1)
    
    total_time = time.time() - start_time
    print(f'Total Time: {total_time} seconds')

    # Salva o texto reconhecido em um arquivo .txt / Save the recognized text to a .txt file
    transcript_file = video_file.replace('.mp4', '.txt')
    with open(transcript_file, 'w') as f:
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
