from whisper_live.client import TranscriptionClient
client = TranscriptionClient(
  "localhost",
  9090,
  lang="zh",
  translate=False,
  use_vad=False,
)
client()