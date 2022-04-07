from google.cloud import storage
import io
import scipy
import os
import soundfile as sf


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\iagg1\Downloads\hackathon-team-07-8d5ab0d8c03e.json"
client = storage.Client()
BUCKET = client.bucket('hackathon-team-07.appspot.com')

def get_file_from_bucket(blob_name):
    blob_loc = BUCKET.blob(blob_name)
    blob_byte = blob_loc.download_as_string()

    return blob_byte

def save_wave_from_byte(bytes, filename):
    output, samplerate = sf.read(io.BytesIO(bytes))
    scipy.io.wavfile.write(filename, samplerate, output)

def save_file_from_gcloud(blob_name,filename):
    bytes = get_file_from_bucket(blob_name)
    save_wave_from_byte(bytes, filename)

def write_to_cloud(blob_name,filename):
    blob = BUCKET.blob(blob_name)
    blob.upload_from_filename(filename)
