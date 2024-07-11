from whisper_live.client import TranscriptionClient
client = TranscriptionClient(
  "172.16.108.68",
  9090,
  lang="zh",
  translate=False,
  use_vad=False,
)
client()