import argparse
import os
from pathlib import Path



from Real_Time_Voice_Cloning.encoder import inference as encoder
from Real_Time_Voice_Cloning.synthesizer.inference import Synthesizer
from Real_Time_Voice_Cloning.utils.default_models import ensure_default_models
from Real_Time_Voice_Cloning.vocoder import inference as vocoder
from app.config import enc_model_fpath,syn_model_fpath, voc_model_fpath

def setup():
    # Set up to use only CPU
    ensure_default_models(Path("saved_models"))
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    encoder.load_model(enc_model_fpath)
    vocoder.load_model(voc_model_fpath)