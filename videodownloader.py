#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author :  ELFO

import os
import subprocess
import glob
import configparser
import sys
from pathlib import Path

def load_config():
    """Lädt die Konfiguration oder erstellt eine neue"""
    config = configparser.ConfigParser()
    config_file = Path.home() / '.config' / 'ytdownloader' / 'config.ini'

    # Erstelle Verzeichnis wenn es nicht existiert
    config_file.parent.mkdir(parents=True, exist_ok=True)

    if config_file.exists():
        config.read(config_file)
    else:
        config['DEFAULT'] = {
            'cookies_file': '',
        }
        with open(config_file, 'w') as f:
            config.write(f)

    return config, config_file

def setup_cookies():
    """Konfiguriert den Pfad zur Cookies-Datei"""
    config, config_file = load_config()

    current_cookies = config['DEFAULT'].get('cookies_file', '')
    print(f"\nAktuelle Cookies-Datei: {current_cookies or 'Nicht konfiguriert'}")

    change = input("Möchtest du den Pfad zur Cookies-Datei ändern? (j/n): ")
    if change.lower() == 'j':
        new_path = input("Gib den vollständigen Pfad zur cookies.txt ein: ")
        if os.path.exists(new_path):
            config['DEFAULT']['cookies_file'] = new_path
            with open(config_file, 'w') as f:
                config.write(f)
            print("Cookies-Pfad erfolgreich aktualisiert!")
        else:
            print("Fehler: Die angegebene Datei existiert nicht!")

    return config['DEFAULT'].get('cookies_file', '')

def convert_to_wav(video_file):
    """Konvertiert Video in WAV-Format für Audio-CD"""
    try:
        output_file = os.path.splitext(video_file)[0] + '.wav'
        subprocess.run([
            'ffmpeg', '-i', video_file,
            '-vn',  # Keine Video-Streams
            '-acodec', 'pcm_s16le',  # CD-Quality Audio
            '-ar', '44100',  # Sample Rate für Audio-CD
            '-ac', '2',  # Stereo
            output_file
        ], check=True)
        print(f"Erfolgreich konvertiert zu: {output_file}")
        return output_file
    except subprocess.CalledProcessError:
        print("Fehler bei der Konvertierung.")
        return None

def convert_to_mp3(video_file):
    """Konvertiert Video in MP3-Format"""
    try:
        output_file = os.path.splitext(video_file)[0] + '.mp3'
        subprocess.run([
            'ffmpeg', '-i', video_file,
            '-vn',  # Keine Video-Streams
            '-acodec', 'libmp3lame',  # MP3 Codec
            '-ab', '320k',  # Bitrate
            '-ar', '44100',  # Sample Rate
            '-ac', '2',  # Stereo
            output_file
        ], check=True)
        print(f"Erfolgreich konvertiert zu: {output_file}")
        return output_file
    except subprocess.CalledProcessError:
        print("Fehler bei der Konvertierung.")
        return None

def convert_audio(video_file, format_type):
    """Konvertiert Video in das gewählte Audioformat"""
    if format_type == "mp3":
        return convert_to_mp3(video_file)
    else:  # wav für Audio-CD
        return convert_to_wav(video_file)

def main():
    print("\n=== Videodownloader and converter by Elfo === "
    )

    # Cookies-Setup
    print("\n=== Für YouTube mit Cookies-Unterstützung ===")
    cookies_file = setup_cookies()

    while True:
        url = input("\nVideo-URL eingeben (oder 'q' zum Beenden): ")

        if url.lower() == 'q':
            break

        # Download-Kommando vorbereiten
        download_cmd = ["yt-dlp", "-f", "b"]

        # Füge Cookies hinzu, wenn konfiguriert
        if cookies_file:
            download_cmd.extend(["--cookies", cookies_file])

        download_cmd.append(url)

        # Video herunterladen
        try:
            subprocess.run(download_cmd, check=True)
            print("Video erfolgreich heruntergeladen.")

            # Finde das zuletzt heruntergeladene Video
            video_files = glob.glob("*.mp4") + glob.glob("*.webm") + glob.glob("*.mkv")
            if video_files:
                latest_video = max(video_files, key=os.path.getctime)
                print(f"Gefundenes Video: {latest_video}")

                # Frage nach dem gewünschten Format
                print("\nIn welches Format möchtest du das Video konvertieren?")
                print("1: MP3")
                print("2: Audio-CD Format (WAV)")
                format_choice = input("Wähle 1 oder 2: ")

                if format_choice in ['1', '2']:
                    format_type = "mp3" if format_choice == '1' else "wav"
                    audio_file = convert_audio(latest_video, format_type)
                    if audio_file:
                        print("\nKonvertierung abgeschlossen!")
                        print(f"Die Audiodatei wurde erstellt: {audio_file}")
                        if format_type == "wav":
                            print("Du kannst diese Datei nun mit deinem bevorzugten CD-Brennprogramm brennen.")
                else:
                    print("Ungültige Auswahl.")
            else:
                print("Keine Video-Datei gefunden.")

        except subprocess.CalledProcessError:
            print("Fehler beim Herunterladen des Videos.")

        another = input("\nMöchtest du ein weiteres Video herunterladen? (j/n): ")
        if another.lower() != 'j':
            break

if __name__ == "__main__":
    main()
