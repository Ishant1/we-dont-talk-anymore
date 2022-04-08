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
from google.cloud import storage

HERE = Path(__file__).parent

logger = logging.getLogger(__name__)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

st.session_state["upload_complete"] = False
st.session_state["user_input"] = ""

def send_audio_and_text(audio_file_id: str, text: str) -> str:
    st.session_state['uuid_to_read'] = "0c18e3b5-f209-45de-9096-f0b4d4b413a7" #TODO: CHANGE THIS WITH API UUID
    # return audio_file_id, text
    # api call(file_id, text)
    # api read wav file, return wav file sounding like origin text but saying `text`
    # should return uuid of generated audio
    display_audio()


def upload_to_bucket(bucket_name, source_file, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    # storage_client = storage.Client.from_service_account_json(
    #     "hackathon-team-07-904256b7513d.json")
    # bucket = storage_client.bucket(bucket_name)
    # blob = bucket.blob(destination_blob_name)

    # blob.upload_from_filename(source_file)

    # print(
    #     "File uploaded to {}.".format(
    #         destination_blob_name
    #     )
    # )

def app_sst():
    """
    Records audio and uploads this to a bucket
    """
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
            break

    audio_buffer = st.session_state["audio_buffer"]

    if not webrtc_ctx.state.playing and len(audio_buffer) > 0:
        # st.info("Writing wav to disk")
        uuid_str = uuid4()
        st.session_state["uuid_str"] = uuid_str
        audio_buffer.export(rf"recordings/{uuid_str}.wav", format="wav")
        upload_to_bucket('hackathon-team-07.appspot.com', f'recordings/{uuid_str}.wav', f'{uuid_str}.wav')

        # Reset
        st.session_state["audio_buffer"] = pydub.AudioSegment.empty()
        st.session_state["upload_complete"] = True

def enter_text():
    st.session_state["user_input"] = st.text_input(label='What do you want to hear yourself say?',
                        value='We don\'t talk anymore',
                        key='text-input-for-speech',
                        )
    
def submit_audio_and_text():
    st.button(label='Submit',
                key='submit-audio-text-button',
                help='Generate your audio file!',
                on_click=send_audio_and_text,
                args=(st.session_state["uuid_str"], st.session_state["user_input"])
                )

def display_audio():
# This is the widget to display the imitated recording. We will remove the other stuff and display this afterwards.
    # send_audio_and_text()
    base_url = 'https://storage.googleapis.com/hackathon-team-07.appspot.com'
    audio_url = f'{base_url}/{st.session_state["uuid_to_read"]}.wav'
    st.audio(data=audio_url, format="audio/wav")
    

#***********************************************************************************#
def main():
    st.image('images\MV5BOWQyYmJiOWUtNzkzYS00YWJlLWI5YjgtYTg4MjI0MmM1N2ZkXkEyXkFqcGdeQXVyNjE0ODc0MDc@._V1_1.jpg')
    st.header("We Don't Talk Anymore")
    st.markdown(
        """
Tired of saying the same thing at Stand Up everyday? Want to ask for a raise but you're to nervous? Need to impersonate your Line Manager giving you great feedback? 

We can imitate a voice from a recording of a few seconds, to satsify all your speaking needs.

Press Start to begin recording...
"""
    )
    app_sst()
    if st.session_state["upload_complete"] == True:
        enter_text()
        submit_audio_and_text()


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
