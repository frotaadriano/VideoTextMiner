**VideoTextMiner** is a powerful tool for extracting text from videos. It uses advanced speech recognition technologies to convert video audio into accurate, readable text. Perfect for content creators, researchers, and anyone needing efficient video transcription.

## Features

- Extracts audio from video files
- Converts audio to text using Azure Speech to Text
- Saves transcript to a .txt file
- FastAPI integration for easy video submission
- Ready method for OpenAI RAG integration

## Requirements

- Python 3.6+
- `pydub`
- `tqdm`
- `azure-cognitiveservices-speech`
- `python-dotenv`
- `fastapi`
- `uvicorn`
- `ffmpeg` (must be installed separately)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/frotaadriano/VideoTextMiner.git
   cd VideoTextMiner

2. Install the required Python packages:
   pip install -r requirements.txt

3. Install ffmpeg:
- For Windows, download from FFmpeg and add to your PATH.
- For macOS, use Homebrew:
brew install ffmpeg
- For Linux, use your package manager:
sudo apt-get install ffmpeg
4. Create a .env file in the root directory and add your Azure subscription key and service region:
AZURE_SUBSCRIPTION_KEY=YourAzureSubscriptionKey
AZURE_SERVICE_REGION=YourAzureServiceRegion

## Usage
- To Run single script
Place your video file in the 'video' project directory.
Run the script executing: python Example1.py

- Run the FastAPI application:
python -m uvicorn main:app --reload
http://127.0.0.1:8000/docs#



## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements
Azure Cognitive Services
FFmpeg
pydub
tqdm
python-dotenv







