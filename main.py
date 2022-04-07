import argparse
import os
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch

from Real_Time_Voice_Cloning.encoder import inference as encoder
from Real_Time_Voice_Cloning.synthesizer.inference import Synthesizer
from Real_Time_Voice_Cloning.utils.default_models import ensure_default_models
from Real_Time_Voice_Cloning.vocoder import inference as vocoder


#Set up to use only CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

#system variables
args = {
    "enc_model_fpath" : "saved_models/default/encoder.pt",
    "syn_model_fpath": "saved_models/default/synthesizer.pt",
    "voc_model_fpath": "saved_models/default/vocoder.pt"
}

# Inputs
FILE_PATH = r"C:\dev\data\northern-english-male\nom_00610_00161421677.wav"
TEXT = 'We are team 7, and today we will be presenting on our hackathon project'


print("Running a test of your configuration...\n")


## Load the models one by one.
print("Preparing the encoder, the synthesizer and the vocoder...")
ensure_default_models(Path("saved_models"))
encoder.load_model(args['enc_model_fpath'])
synthesizer = Synthesizer(args['syn_model_fpath'])
vocoder.load_model(args['voc_model_fpath'])


num_generated = 0
try:
    # Get the reference audio filepath
    # message = "Reference voice: enter an audio filepath of a voice to be cloned (mp3, " \
    #           "wav, m4a, flac, ...):\n"
    # in_fpath = Path(input(message).replace("\"", "").replace("\'", ""))

    ## Computing the embedding
    # First, we load the wav using the function that the speaker encoder provides. This is
    # important: there is preprocessing that must be applied.

    # The following two methods are equivalent:
    # - Directly load from the filepath:
    # preprocessed_wav = encoder.preprocess_wav(FILE_PATH)
    # - If the wav is already loaded:
    original_wav, sampling_rate = librosa.load(str(FILE_PATH))
    preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)
    print("Loaded file succesfully")

    # Then we derive the embedding. There are many functions and parameters that the
    # speaker encoder interfaces. These are mostly for in-depth research. You will typically
    # only use this function (with its default parameters):
    embed = encoder.embed_utterance(preprocessed_wav)
    print("Created the embedding")


    # The synthesizer works in batch, so you need to put your data in a list or numpy array
    texts = [TEXT]
    embeds = [embed]
    # If you know what the attention layer alignments are, you can retrieve them here by
    # passing return_alignments=True
    specs = synthesizer.synthesize_spectrograms(texts, embeds)
    spec = specs[0]
    print("Created the mel spectrogram")


    ## Generating the waveform
    print("Synthesizing the waveform:")


    # Synthesizing the waveform is fairly straightforward. Remember that the longer the
    # spectrogram, the more time-efficient the vocoder.
    generated_wav = vocoder.infer_waveform(spec)


    ## Post-generation
    # There's a bug with sounddevice that makes the audio cut one second earlier, so we
    # pad it.
    generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")

    # Trim excess silences to compensate for gaps in spectrograms (issue #53)
    generated_wav = encoder.preprocess_wav(generated_wav)

    # Save it on the disk
    filename = "demo_output_%02d.wav" % num_generated
    print(generated_wav.dtype)
    sf.write(filename, generated_wav.astype(np.float32), synthesizer.sample_rate)
    num_generated += 1
    print("\nSaved output as %s\n\n" % filename)


except Exception as e:
    print("Caught exception: %s" % repr(e))
    print("Restarting\n")
