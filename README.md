# Chinese Story Practice

CSP is a desktop application made in PyQt6 for practicing the Chinese homework my teachers at Toronto Chinese Academy give me. It's based on a folder structure of lessons, where each lesson has:
- "story.pdf": a pdf file containing the story to be practiced
- "story.txt": a txt file containing the pinyin/characters of the story to be practiced
- "homework.txt": a txt file containing the written homework I will be writing
- "story.m4a"/"story.mp3": an audio file containing the audio for the story I am practicing.
- "log.txt": a txt file containing the log of how long it takes me to say the story.

## Code Structure
- csp.py contains the main application
- CustomWidgets.py contains the custom widgets I made
- config.ini contains teh configuration information.