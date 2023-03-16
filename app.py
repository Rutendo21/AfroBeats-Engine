from flask import Flask, render_template, request
import csv
import os
import lyricsgenius

genius = lyricsgenius.Genius('fu-Qcgs1IoyfYwlgxbe2_KZkLaV7fLxCQkZxaVwOQ0ovibQJMHOSyLivmtGNQWnd', remove_section_headers = True, timeout=120)

app = Flask(__name__)

@app.route("/")
def homepage():
    
    if request.method == "GET":
        Artists = []
        file = open("AfroBeatsArtists.csv", "r")
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            Artist = row
            Artists.append(Artist)
        
        return render_template("index.html", Artists=Artists)

def main(Artist):
    
    File, FilePath, SongTitles, ThemeWords, Sounds = LoadData(Artist)
    
def LoadData(Artist):
    
    Sounds = []
    ThemeWords = []
    SongTitles = []
    
    Path = os.getcwd()
    Directoryname = '\LyricsByArtist'
    DirectoryPath = Path + Directoryname + '\\'
    
    Filename = Artist + '.txt'
    FilePath = DirectoryPath + Filename
    if os.path.exists(FilePath):
        pass
    else:
        with open(FilePath, 'w' , encoding='utf-8') as File:
            ArtistSongs = genius.search_artist(Artist, sort='title', include_features=True)
            Songs = ArtistSongs.songs
            for Song in Songs:
                SongTitles.append(Song.title)
                SongLyrics = Song.lyrics
                File.write(SongLyrics)
                File.write('\n \n \n')
        File.close()
    
    with open(FilePath, 'r', encoding='utf-8') as File:
        FileContent = File.readlines()
    File.close()
    
    with open(FilePath, 'r', encoding='utf-8') as File:
        for Line in File:
            if Line.strip():
                Words = (Line.split(" "))
                WordCount = len(Words)
                if WordCount > 3:
                    for i in range(WordCount - 2):
                        Word1 = Words[i].lower()
                        Word2 = Words[i + 1].lower()
                        Word3 = Words[i + 2].lower()
                        if Word1 == Word2 == Word3:
                            Word = Word1.split(",")
                            Word = Word[0]
                            if Word not in Sounds:
                                Sounds.append(Word)
                if WordCount > 2:          
                    for i in range(WordCount - 1):
                        Word1 = Words[i].lower()
                        Word2 = Words[i + 1].lower()
                        if Word1 == Word2:
                            Word = Word1.split(",")
                            Word = Word[0]
                            if Word not in Sounds and Word not in ThemeWords: 
                                ThemeWords.append(Word)
    File.close()
    
    return FileContent, FilePath, SongTitles, ThemeWords, Sounds

if __name__ == "__main__":
    app.run()
    