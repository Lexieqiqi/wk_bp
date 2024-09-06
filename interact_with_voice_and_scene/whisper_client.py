import requests
import argparse

def transcribe_audio(file_path, server_url):
    with open(file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post(server_url, files=files)
    
    if response.status_code == 200:
        transcription = response.json().get('transcription', 'No transcription found')
        print("Transcription:", transcription)
    else:
        print("Error:", response.status_code, response.json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio files using a remote Whisper server.")
    parser.add_argument('file_path', type=str, help='Path to the audio file.')
    parser.add_argument('server_url', type=str, default=' http://172.16.108.68:5000/transcribe',  help='URL of the transcription server.')

    args = parser.parse_args()
    transcribe_audio(args.file_path, args.server_url)
