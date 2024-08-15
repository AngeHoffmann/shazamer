import os
import asyncio
from pydub import AudioSegment
from shazamio import Shazam
from tqdm import tqdm

async def recognize_segment(segment_file):
    shazam = Shazam()
    try:
        out = await shazam.recognize(segment_file)
        if out['matches']:
            song_info = out['track']
            song_title = song_info['title']
            song_artist = song_info['subtitle']
            return song_title, song_artist
    except Exception as e:
        print(f"Error recognizing segment: {e}")
    return None, None

def split_audio(file_path, segment_length_ms):
    audio = AudioSegment.from_file(file_path)
    segments = [audio[i:i + segment_length_ms] for i in range(0, len(audio), segment_length_ms)]
    return segments

def format_time(seconds):
    seconds = int(seconds)
    if seconds < 3600:
        return f"{seconds // 60}:{seconds % 60:02}"
    else:
        return f"{seconds // 3600}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"

async def main(audio_file):
    segment_length = 30000  # Длина сегмента в миллисекундах (например, 60 секунд)
    segments = split_audio(audio_file, segment_length)

    results = []

    for i, segment in enumerate(tqdm(segments, desc="Processing segments")):
        segment_file = f"segment_{i}.mp3"
        segment.export(segment_file, format="mp3")
        song_title, song_artist = await recognize_segment(segment_file)
        start_time = i * segment_length / 1000  # Время начала сегмента в секундах
        if song_title and song_artist:
            results.append({
                'start_time': start_time,
                'title': song_title,
                'artist': song_artist
            })
		# Удаление сегментированного файла
        os.remove(segment_file)

    # Вывод результатов
    for result in results:
        formatted_time = format_time(result['start_time'])
        print(f"{formatted_time} {result['artist']} - {result['title']}")

if __name__ == "__main__":
    # Получаем текущую рабочую директорию
    current_directory = os.getcwd()
    
    # Абсолютный путь к файлу
    audio_file = os.path.join(current_directory, "audio_file.mp3")
    print(f"Audio File Path: {audio_file}")
    
    asyncio.run(main(audio_file))
