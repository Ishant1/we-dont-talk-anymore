from typing import Optional
import numpy as np
import soundfile as sf

from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from fastapi import FastAPI

from app.config import syn_model_fpath
from app.setup import setup
from app.utils import save_file_from_gcloud
from Real_Time_Voice_Cloning.encoder import inference as encoder
from Real_Time_Voice_Cloning.synthesizer.inference import Synthesizer
from Real_Time_Voice_Cloning.vocoder import inference as vocoder



app = FastAPI()

@app.get("/buildaudio")
def buildaudio(blob_name: str, text: str, local: Optional[int] = 1):

    loc = 'sample.wav'
    save_file_from_gcloud(blob_name,loc)
    setup()

    # Load the Input
    if local>0:
        synthesizer = Synthesizer(syn_model_fpath)
        preprocessed_wav = encoder.preprocess_wav(loc)
        embed = encoder.embed_utterance(preprocessed_wav)

        texts = [text]
        embeds = [embed]
        specs = synthesizer.synthesize_spectrograms(texts, embeds)
        spec = specs[0]

        generated_wav = vocoder.infer_waveform(spec)

        ## Post-generation
        # There's a bug with sounddevice that makes the audio cut one second earlier, so we
        # pad it.
        generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")

        # Trim excess silences to compensate for gaps in spectrograms (issue #53)
        generated_wav = encoder.preprocess_wav(generated_wav)

        # Save it on the disk
        filename = "demo_output_%02d.wav" % 1
        sf.write(filename, generated_wav.astype(np.float32), synthesizer.sample_rate)
        return status.HTTP_200_OK

    else:
        return status.HTTP_400_BAD_REQUEST


