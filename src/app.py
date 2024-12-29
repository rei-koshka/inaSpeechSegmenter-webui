from inaSpeechSegmenter_webui.helpers import get_gendered_segments_overall
from inaSpeechSegmenter_client.segmenter_client import SegmenterClient

import logging

from os import environ
from typing import List, cast

import streamlit as st

from streamlit.runtime.uploaded_file_manager import UploadedFile

api_url = environ.get("INA_SPEECH_SEGMENTER_API_URL", "http://127.0.0.1:8888")
log_level = environ.get("INA_SPEECH_SEGMENTER_WEBUI_LOG_LEVEL", "DEBUG")

logger = logging.Logger(
    name=__name__,
    level=getattr(logging, log_level),
)

segmenter_client = SegmenterClient(
    api_url=api_url,
)

app_name = "inaSpeechSegmenter webui"

st.set_page_config(
    page_title=app_name,
)

st.title(app_name)

audio_files_uploaded = st.file_uploader(
    label="Audio files",
    accept_multiple_files=True,
    type=[
        "mp3",
        "wav",
        "m4a",
        "ogg",
        "amr",
    ]
)

audio_files_recorded: List[UploadedFile | None]  = []

audio_file_recorded = st.audio_input(
    label="Record",
    key=f"audio_recorder_0",
)

audio_files_recorded.append(audio_file_recorded)

audio_files_all: List[UploadedFile] = []

for audio_file in audio_files_recorded:
    if audio_file is not None:
        audio_files_all.append(audio_file)

if audio_files_uploaded is not None:
    if isinstance(audio_files_uploaded, list):
           for audio_file in audio_files_uploaded:
               audio_files_all.append(audio_file)
    elif isinstance(audio_files_uploaded, UploadedFile):
        audio_files_all.append(audio_files_uploaded)

if st.button(
    label="Analyze",
    type="primary",
    use_container_width=True,
):
    for audio_file in audio_files_all:
        with st.spinner("Analyzing..."):
            audio_file_name = audio_file.name
            audio_bytes = audio_file.getbuffer()

            try:
                response_data = segmenter_client.get_segments(
                    audio_file_name=audio_file_name,
                    audio_bytes=audio_bytes,
                )

                with st.container(border=True):
                    col1, col2 = st.columns(2)

                    col1.text(audio_file.name)
                    col1.audio(audio_file)

                    overall = get_gendered_segments_overall(response_data)

                    for overall_item in overall:
                        label = cast(str, overall_item.label)
                        ratio = float(overall_item.ratio)

                        col2.metric(
                            label=label.capitalize(),
                            value=f"{ratio:.1%}",
                        )

                    with st.expander(
                        label="Details",
                        expanded=False,
                    ):
                        st.json(
                            body=response_data.model_dump_json(),
                            expanded=True,
                        )
            except Exception as exception:
                st.error(exception)
                logger.error(exception)
