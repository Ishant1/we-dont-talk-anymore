import logging.handlers
import os
import queue
from pathlib import Path
from uuid import uuid4

import pydub
import streamlit as st
from streamlit_webrtc import (
    WebRtcMode,
    RTCConfiguration,
    webrtc_streamer,
)

HERE = Path(__file__).parent

logger = logging.getLogger(__name__)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


def send_audio_and_text(audio_file_id: str, text: str) -> None:
    pass


def main():
    st.header("We don't talk anymore")
    st.markdown(
        """
This demo app from We don't talk anymore ™️.
It can imitate your voice from a recording of a few seconds and say whatever you want it to say.
"""
    )
    app_sst()
    st.text_input(label='What do you want to hear yourself say?',
                  value='We don\'t talk anymore',
                  key='text-input-for-speech')
    st.button(label='Submit text and recording of my voice',
              key='submit-audio-text-button',
              help='Generate your audio file!',
              on_click=send_audio_and_text,
              )
    # This is the widget to display the imitated recording. We will remove the other stuff and display this afterwards.
    # st.audio(data=audio_file, format="audio/wav")


def app_sst():
    webrtc_ctx = webrtc_streamer(
        key="some-unique-key",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=256,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": False, "audio": True},
    )

    if "audio_buffer" not in st.session_state:
        st.session_state["audio_buffer"] = pydub.AudioSegment.empty()

    status_indicator = st.empty()

    while True:
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                status_indicator.write("No frame arrived.")
                continue

            status_indicator.write("Running. Say something!")

            sound_chunk = pydub.AudioSegment.empty()
            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if len(sound_chunk) > 0:
                st.session_state["audio_buffer"] += sound_chunk
        else:
            status_indicator.write("AudioReciver is not set. Abort.")
            break

    audio_buffer = st.session_state["audio_buffer"]

    if not webrtc_ctx.state.playing and len(audio_buffer) > 0:
        st.info("Writing wav to disk")
        audio_buffer.export(rf"recordings/{uuid4()}.wav", format="wav")

        # Reset
        st.session_state["audio_buffer"] = pydub.AudioSegment.empty()


if __name__ == "__main__":

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
