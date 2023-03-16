from flask import Flask, render_template, request
import csv
import os
import lyricsgenius
import markovify
import random
import nltk
import string

UPLOAD_FOLDER = "LyricsByArtist"
application = Flask(__name__)
application.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
application.config["TEMPLATES_AUTO_RELOAD"] = True

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
    
    StopWords = nltk.corpus.stopwords.words("english")
    
    ThemeWord, ThemeSound = Theme(SongTitles, ThemeWords, Sounds)
    
    ArtistSongs = open(FilePath, 'r', encoding='utf-8')
    ArtistSongsContent = ArtistSongs.readlines()
    ArtistSongs.close()
    
    TextModel = markovify.NewlineText(File, state_size=3)
    TextModel = TextModel.compile()
    
    FirstLines = PossibleOpenings(TextModel, ArtistSongsContent)
    
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

def Theme(SongTitles, ThemeWords, Sounds):
    
    while True:
        RandomChoiceThemeWord = random.choice(ThemeWords)
        Quit = 0
        if RandomChoiceThemeWord in Sounds:
            Quit = 1
        for SongTitle in SongTitles:
            if RandomChoiceThemeWord in SongTitle.lower():
                Quit = 1
        if Quit == 0:
            break
        
    RandomChoiceSound = random.choice(Sounds)
        
    return RandomChoiceThemeWord, RandomChoiceSound


def PossibleOpenings(TextModel, ArtistSongsContent):
    
    FirstLines = []  

    for i in range(50):
        PossibleOpenings = FirstLines
        while True:
            while True:
                FirstLine = TextModel.make_short_sentence(70)
                if FirstLine != None:
                    Quit = 0
                    Words = {}
                    AllWords = []
                    ActualWords = tokenize(FirstLine, StopWords=[])
                    FirstLineWords = (FirstLine.split(" "))
                    FirstLineWordsCount = len(FirstLineWords)
                    for i in range(FirstLineWordsCount):
                        Word = FirstLineWords[i].split(",")
                        Word = Word[0].lower()
                        AllWords.append(Word)
                else:
                    continue
                    
                for ActualWord in ActualWords:
                    Words[ActualWord] = 0
                    for Word in AllWords:
                        if ActualWord == Word:
                            Words[ActualWord] += 1
                        if Words[ActualWord] > 3:
                            Quit = 1
                            
                if Quit > 0:
                    continue
                else:
                    PhrasesCount = 0
                    if FirstLine != None:
                        Phrases = FirstLine.split(",")
                        PhrasesCount = len(Phrases)
                    if PhrasesCount > 1:
                        continue
                    else:
                        break
                
            if FirstLine not in PossibleOpenings and FirstLine != None and FirstLine not in ArtistSongsContent:
                break
            else:
                continue
                    
        FirstLines.append(FirstLine.capitalize())
                    
    return FirstLines


def tokenize(Sentence, StopWords):
    
    SentenceWords = []

    words = nltk.tokenize.word_tokenize(Sentence)
    for word in words:
        word = word.lower()
        punctuations = string.punctuation
        if word not in StopWords and word not in punctuations and word not in SentenceWords:
            SentenceWords.append(word)
        
    return SentenceWords


if __name__ == "__main__":
    app.run()
    