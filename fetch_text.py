import re
import sys
import subprocess
import tempfile
import os

def download_subtitles(youtube_link, language='en'):
    with tempfile.TemporaryDirectory() as tmpdir:
        command = [
            'yt-dlp', '--write-auto-subs', '--skip-download', '--sub-lang', language,
            '--output', os.path.join(tmpdir, 'video'), youtube_link
        ]
        subprocess.run(command, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Find the downloaded subtitle file
        for filename in os.listdir(tmpdir):
            if filename.endswith('.vtt'):
                with open(os.path.join(tmpdir, filename), 'r', encoding='utf-8') as file:
                    return file.read()
    return None


def clean_subtitles(subtitle_text):
    # Remove WEBVTT header and metadata
    subtitle_text = re.sub(r'WEBVTT.*?\n', '', subtitle_text, flags=re.DOTALL)
    subtitle_text = re.sub(r'Kind:.*?\n', '', subtitle_text)
    subtitle_text = re.sub(r'Language:.*?\n', '', subtitle_text)

    # Remove timestamps and formatting tags
    subtitle_text = re.sub(
        r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', subtitle_text)
    # Remove <c> and other tags
    subtitle_text = re.sub(r'<.*?>', '', subtitle_text)

    # Remove empty lines and unnecessary spaces
    subtitle_text = re.sub(r'\n+', '\n', subtitle_text).strip()

    # Remove duplicate lines
    lines = subtitle_text.split('\n')
    unique_lines = list(dict.fromkeys(lines))
    subtitle_text = '\n'.join(unique_lines)

    return subtitle_text


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: fetch-text <youtube_link> [language_code]")
        print("Example: fetch-text https://youtube.com/watch?v=xxx en")
        print("Default language is 'en' if not specified")
        sys.exit(1)

    youtube_link = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) == 3 else 'en'

    try:
        subtitle_text = download_subtitles(youtube_link, language)
        if subtitle_text:
            cleaned_text = clean_subtitles(subtitle_text)
            print(cleaned_text)
        else:
            print(f"Failed to download subtitles or no subtitles available for language: {language}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading subtitles: {e}")
        sys.exit(1)
