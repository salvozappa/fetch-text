#!/usr/bin/env python3
# test_subtitle_downloader.py

import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import tempfile
import subprocess
from fetch_text import download_subtitles, clean_subtitles

class TestSubtitleDownloader(unittest.TestCase):
    def setUp(self):
        self.sample_vtt = """WEBVTT
Kind: captions
Language: en

00:00:00.000 --> 00:00:02.000
<c.text>Hello world</c.text>

00:00:02.000 --> 00:00:04.000
<c.text>This is a test</c.text>

00:00:04.000 --> 00:00:06.000
<c.text>Hello world</c.text>
"""
        self.expected_clean_output = "Hello world\nThis is a test"

    @patch('tempfile.TemporaryDirectory')
    @patch('subprocess.run')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_subtitles_success(self, mock_file, mock_listdir, mock_subprocess, mock_tempdir):
        # Setup mocks
        mock_tempdir.return_value.__enter__.return_value = '/temp'
        mock_listdir.return_value = ['video.en.vtt']
        mock_file.return_value.__enter__.return_value.read.return_value = self.sample_vtt
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Test
        result = download_subtitles('https://youtube.com/watch?v=test', 'en')
        
        # Assertions
        self.assertEqual(result, self.sample_vtt)
        mock_subprocess.assert_called_once()
        mock_listdir.assert_called_once_with('/temp')
        mock_file.assert_called_once()

    @patch('tempfile.TemporaryDirectory')
    @patch('subprocess.run')
    @patch('os.listdir')
    def test_download_subtitles_no_vtt_file(self, mock_listdir, mock_subprocess, mock_tempdir):
        # Setup mocks
        mock_tempdir.return_value.__enter__.return_value = '/temp'
        mock_listdir.return_value = ['video.mp4']  # No VTT file
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Test
        result = download_subtitles('https://youtube.com/watch?v=test', 'en')
        
        # Assertions
        self.assertIsNone(result)
        mock_subprocess.assert_called_once()
        mock_listdir.assert_called_once_with('/temp')

    @patch('subprocess.run')
    def test_download_subtitles_subprocess_error(self, mock_subprocess):
        # Setup mock to raise CalledProcessError
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'yt-dlp')

        # Test
        with self.assertRaises(subprocess.CalledProcessError):
            download_subtitles('https://youtube.com/watch?v=test', 'en')

    def test_clean_subtitles(self):
        # Test normal cleaning
        result = clean_subtitles(self.sample_vtt)
        self.assertEqual(result, self.expected_clean_output)

    def test_clean_subtitles_empty_input(self):
        # Test with empty input
        result = clean_subtitles("")
        self.assertEqual(result, "")

    def test_clean_subtitles_no_metadata(self):
        # Test with VTT content but no metadata
        sample = """00:00:00.000 --> 00:00:02.000
<c.text>Test line</c.text>"""
        expected = "Test line"
        result = clean_subtitles(sample)
        self.assertEqual(result, expected)

    def test_clean_subtitles_complex_tags(self):
        # Test with complex formatting tags
        sample = """WEBVTT

00:00:00.000 --> 00:00:02.000
<c.color.cyan><b>Complex</b></c> <i>formatting</i>

00:00:02.000 --> 00:00:04.000
<c.bg_red>More</c> <u>tests</u>"""
        expected = "Complex formatting\nMore tests"
        result = clean_subtitles(sample)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()