# Fetch Text

Download text captions from YouTube, strip them from any metadata and output them to the output stream.
I use this to quickly copy the content of a YouTube video to an LLM.

## Usage

To use the cli:

```sh
fetch-text <youtube_link> [language_code]
```

Example:

```sh
example fetch-text https://youtube.com/watch?v=mL0crkf5Dzw en > video_transcription.txt
```

## Test

```sh
python -m unittest test_fetch_text.py -v
```
