import logging
import logging.handlers
import queue
import threading
import time
import urllib.request
from collections import deque
from pathlib import Path
from typing import List

import av
import numpy as np
import pydub
import streamlit as st

from streamlit_webrtc import (
    AudioProcessorBase,
    ClientSettings,
    WebRtcMode,
    RTCConfiguration,
    webrtc_streamer,
)

HERE = Path(__file__).parent

logger = logging.getLogger(__name__)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

def main():
    st.header("Real Time Speech-to-Text")
    st.markdown(
        """
This demo app is using [DeepSpeech](https://github.com/mozilla/DeepSpeech),
an open speech-to-text engine.
A pre-trained model released with
[v0.9.3](https://github.com/mozilla/DeepSpeech/releases/tag/v0.9.3),
trained on American English is being served.
"""
    )

    sound_chunk = app_sst()
    return sound_chunk

def app_sst():
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": False, "audio": True},
        )

    status_indicator = st.empty()

    if not webrtc_ctx.state.playing:
        print('not playing...')
        return
    print('playing...')

    status_indicator.write("Loading...")

    while True:
        if webrtc_ctx.audio_receiver:
            print('audio receiver true')
            sound_chunk = pydub.AudioSegment.empty()
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                print('queue is empty')
                time.sleep(0.1)
                status_indicator.write("No frame arrived.")
                continue

            status_indicator.write("Running. Say something!")

            for audio_frame in audio_frames:
                print(audio_frame)
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if len(sound_chunk) == 0:
                print('sound chunk has no length')
                status_indicator.write("AudioReciver is not set. Abort.")
                break
            else:
                sound_chunk.export(r"C:\Users\WinUser\dev\test.wav", format="wav")
                print("exported wav file")


if __name__ == "__main__":
    import os
    print('***************************')

    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: "
        "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.DEBUG)

    fsevents_logger = logging.getLogger("fsevents")
    fsevents_logger.setLevel(logging.WARNING)

    main()
    # print(f'Output of main() {main()}')