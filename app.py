from flask import Flask, render_template, request
import csv
import os
import lyricsgenius
import markovify
import random
import nltk
import string
import math
import language_tool_python

UPLOAD_FOLDER = "LyricsByArtist"
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["TEMPLATES_AUTO_RELOAD"] = True

genius = lyricsgenius.Genius('fu-Qcgs1IoyfYwlgxbe2_KZkLaV7fLxCQkZxaVwOQ0ovibQJMHOSyLivmtGNQWnd', remove_section_headers = True, timeout=120)

tool = language_tool_python.LanguageTool('en-UK')

@app.route("/", methods=["GET", "POST"])
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
    
    FirstLine = Opening(FirstLines, ArtistSongsContent, ThemeWord, ThemeSound, ThemeWords, Sounds)
    
    Verse = WriteVerse(FirstLine, TextModel, ArtistSongsContent, Sounds, ThemeSound, ThemeWord, StopWords)
    
    FinalVerse = []
    for i in range(len(Verse) - 1):
        i = i + 1
        if i == 1:
            Line = '"' + ' ' + Verse[i].capitalize()
        elif i == 5:
            Line = Verse[i].capitalize() + ' ' + '"'
        else:
            Line = Verse[i].capitalize()
        FinalVerse.append(Line)
    
    return FinalVerse

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

def Grammar(Sentence):
    
    Matches = tool.check(Sentence)
    NumberOfMistakes = len(Matches)
        
    if NumberOfMistakes < 3:
        Words = Sentence.split()
        TaggedSentence = nltk.tag.pos_tag(Words)
        NumberOfCategories = len(TaggedSentence)
            
        VBResult = VB(TaggedSentence, NumberOfCategories)
        VBPResult = VBP(TaggedSentence, NumberOfCategories)
        NNResult = NN(TaggedSentence, NumberOfCategories)
        NNPResult = NNP(TaggedSentence, NumberOfCategories)
        RPResult = RP(TaggedSentence, NumberOfCategories)
        INResult = IN(TaggedSentence, NumberOfCategories)
        RBResult = RB(TaggedSentence, NumberOfCategories)
        PRPResult = PRP(TaggedSentence, NumberOfCategories)
            
        if VBResult == True and VBPResult == True and NNResult == True and NNPResult == True and RPResult == True and INResult == True and RBResult == True and PRPResult == True:
            return True
              
    return False
    
            
def VB(TaggedSentence, NumberOfCategories):
    
    for i in range(NumberOfCategories):
        if TaggedSentence[i][1] == 'VB':
            if i > 0:
                PreviousWordIdentity = TaggedSentence[i - 1][1]   
                if PreviousWordIdentity != 'DT' and PreviousWordIdentity != 'PRP' and PreviousWordIdentity != 'VB' and PreviousWordIdentity != 'VBP' and PreviousWordIdentity != 'WP' and PreviousWordIdentity != 'NNS' and PreviousWordIdentity != 'JJ':
                    return False
    
    return True
            

def VBP(TaggedSentence, NumberOfCategories):
    
    for i in range(NumberOfCategories):
        if TaggedSentence[i][1] == 'VBP':
            if i > 0:
                PreviousWordIdentity = TaggedSentence[i - 1][1]
                if PreviousWordIdentity != 'PRP' and PreviousWordIdentity != 'DT' and PreviousWordIdentity != 'WP' and PreviousWordIdentity != 'NN':
                    return False
    
    return True
            

def NN(TaggedSentence, NumberOfCategories):
    
    for i in range(NumberOfCategories):
        if TaggedSentence[i][1] == 'NN':
            if i > 0:
                PreviousWordIdentity = TaggedSentence[i - 1][1]  
                if PreviousWordIdentity != 'NN' and PreviousWordIdentity != 'NNP' and PreviousWordIdentity != 'DT' and PreviousWordIdentity != 'VB' and PreviousWordIdentity != 'VBP' and PreviousWordIdentity != 'PRP$' and PreviousWordIdentity != 'IN' and PreviousWordIdentity != 'JJ' and PreviousWordIdentity != 'UH':
                    return False
    
    return True


def NNP(TaggedSentence, NumberOfCategories):
    
    for i in range(NumberOfCategories):
        if TaggedSentence[i][1] == 'NNP':
            if i > 0:
                PreviousWordIdentity = TaggedSentence[i - 1][1]       
                if PreviousWordIdentity != 'NNP' and PreviousWordIdentity != 'NN' and PreviousWordIdentity != 'DT':
                    return False
    
    return True


def RP(TaggedSentence, NumberOfCategories):
    
    for i in range(NumberOfCategories):
        if TaggedSentence[i][1] == 'RP':
            if i > 0:
                PreviousWordIdentity = TaggedSentence[i - 1][1]        
                if PreviousWordIdentity != 'PRP' and  PreviousWordIdentity != 'VB':
                    return False
    
    return True


def IN(TaggedSentence, NumberOfCategories):
        
    for i in range(NumberOfCategories):
        if TaggedSentence[i][1] == 'IN':
            if i > 0:
                PreviousWordIdentity = TaggedSentence[i - 1][1]    
                if PreviousWordIdentity != 'NNP' and PreviousWordIdentity != 'NN' and PreviousWordIdentity != 'RB':
                    return False
    
    return True


def RB(TaggedSentence, NumberOfCategories):
    
    for i in range(NumberOfCategories):
        if TaggedSentence[i][1] == 'RB':
            if i > 0:
                PreviousWordIdentity = TaggedSentence[i - 1][1]  
                if PreviousWordIdentity != 'VB' and PreviousWordIdentity != 'PRP' and PreviousWordIdentity != 'RB' and PreviousWordIdentity != 'CC':
                    return False
    
    return True


def PRP(TaggedSentence, NumberOfCategories):
    
    for i in range(NumberOfCategories):
        if TaggedSentence[i][1] == 'PRP':
            if i > 0:
                PreviousWordIdentity = TaggedSentence[i - 1][1]     
                if PreviousWordIdentity != 'PRP' and PreviousWordIdentity != 'NNP' and PreviousWordIdentity != 'IN' and PreviousWordIdentity != 'VB' and PreviousWordIdentity != 'VBP' and PreviousWordIdentity != 'NN':
                    return False
    
    return True


def Opening(FirstLines, ArtistSongsContent, ThemeWord, ThemeSound, ThemeWords, Sounds):
    
    Run = 0
    
    while True:
        while True:
            FirstLine = random.choice(FirstLines)
            Words = FirstLine.split()
            TaggedFirstLine = nltk.tag.pos_tag(Words)
            NumberOfCategories = len(TaggedFirstLine)
            
            Run += 1
            if Run == 50:
                NewSentenceWords =  Words
                break
    
            Theme = []
            Theme.append(ThemeWord)
            Theme.append(ThemeSound)
            TaggedTheme = nltk.tag.pos_tag(Theme)
            ThemeWordCategory = TaggedTheme[0][1]
            ThemeSoundCategory = TaggedTheme[1][1]
    
            NewSentenceWords = []
    
            if ThemeWordCategory == ThemeSoundCategory:
                Replace = []
                for i in range(NumberOfCategories - 2):
                    i = i + 1
                    if TaggedFirstLine[i][1] == ThemeWordCategory and TaggedFirstLine[i - 1][1] != 'NNP':
                        if TaggedFirstLine[i][1] not in Replace:
                            Replace.append(TaggedFirstLine[i][0])
                LengthReplace = len(Replace)
                
                if LengthReplace < 2:
                    continue
                else:
                    Fail = 0
                    while True:
                        ReplacedWord1, ReplacedWord2 = random.choices(Replace, k=2)
                        if ReplacedWord1 == ReplacedWord2:
                            continue
                        if ReplacedWord1 not in Sounds:
                            if ReplacedWord2 in Sounds or ReplacedWord2 in ThemeWords:
                                break
                            else:
                                Fail += 1
                        if Fail == 10:
                            ReplacedWord2Options = []
                            for Word in Words:
                                if Word != ReplacedWord1:
                                    if Word in Sounds or Word in ThemeWords:
                                        ReplacedWord2Options.append(Word)
                            if len(ReplacedWord2Options) > 0:
                                ReplacedWord2 = random.choice(ReplacedWord2Options)
                                Fail += 1
                                break
                            break 
                        
                    if Fail == 10:
                        continue
                    for i in range(NumberOfCategories):
                        if TaggedFirstLine[i][0] == ReplacedWord1:
                            NewSentenceWords.append(ThemeWord)
                        elif TaggedFirstLine[i][0] == ReplacedWord2:
                            NewSentenceWords.append(ThemeSound)
                        else:
                            NewSentenceWords.append(TaggedFirstLine[i][0])
                    break
            else:
                ThemeWordCount = 0
                ThemeWordReplace = []
                ThemeSoundCount = 0
                ThemeSoundReplace = []
        
                for i in range(NumberOfCategories - 2):
                    i = i + 1
                    if TaggedFirstLine[i][1] == ThemeWordCategory and TaggedFirstLine[i - 1][1] != 'NNP':
                        if TaggedFirstLine[i][1] not in ThemeWordReplace:
                            ThemeWordCount = 1
                            ThemeWordReplace.append(TaggedFirstLine[i][0])
                    elif TaggedFirstLine[i][1] == ThemeSoundCategory and TaggedFirstLine[i - 1][1] != 'NNP':
                        if TaggedFirstLine[i][1] not in ThemeSoundReplace:
                            ThemeSoundCount = 1
                            ThemeSoundReplace.append(TaggedFirstLine[i][0])
            
                if ThemeWordCount == 0 and ThemeSoundCount == 0:
                    continue
                else:
                    if ThemeWordCount > 0:
                        while True:
                            RandomWord1 = random.choice(ThemeWordReplace)
                            if RandomWord1 not in Sounds:
                                break
                    if ThemeSoundCount > 0:
                        while True:
                            RandomWord2 = random.choice(ThemeSoundReplace)
                            if RandomWord2 not in ThemeWords:
                                break
                    for i in range(NumberOfCategories):
                        if ThemeWordCount > 0 and TaggedFirstLine[i][0] == RandomWord1:
                            NewSentenceWords.append(ThemeWord)
                        elif ThemeSoundCount > 0 and TaggedFirstLine[i][0] == RandomWord2:
                            NewSentenceWords.append(ThemeSound)
                        else:
                            NewSentenceWords.append(TaggedFirstLine[i][0])
                    break
                
        OpeningLine = ' '.join(NewSentenceWords)
        if OpeningLine not in ArtistSongsContent:
            break
    
    return OpeningLine


def WriteVerse(FirstLine, TextModel, ArtistSongsContent, Sounds, ThemeSound, ThemeWord, StopWords):
    
    Lyrics = []
    PossibleLyrics = []
    PreviousLyric = FirstLine
    Lyrics.append(PreviousLyric)
    LyricsCount = 1
    LengthCount = 0
    
    while LengthCount < 5:
        
        PreviousWords = tokenize(PreviousLyric, StopWords)
        
        for i in range(500):
            PossibleLyric = TextModel.make_sentence(tries=500)
            Result = Grammar(PossibleLyric)
            if Result == True and PossibleLyric not in ArtistSongsContent:
                PossibleLyrics.append(PossibleLyric.lower()) 
        
        IDFs = CalculateIDFs(PreviousWords, PossibleLyrics)
        PreviousLyricTopSentences = TopSentences(PreviousWords, IDFs, PossibleLyrics, StopWords)
        ActualPreviousLyricTopSentences = list(PreviousLyricTopSentences.keys())
        
        for ActualPreviousLyricTopSentence in ActualPreviousLyricTopSentences:
            Quit = 0
            ActualPreviousLyricTopSentenceWords = tokenize(ActualPreviousLyricTopSentence, StopWords)
            for i in range(LyricsCount):
                if ActualPreviousLyricTopSentence == Lyrics[i]:
                    Quit = 1     
            LyricWords = []
            AllActualPreviousLyricTopSentenceWords = (ActualPreviousLyricTopSentence.split(" "))
            AllActualPreviousLyricTopSentenceWordsCount = len(AllActualPreviousLyricTopSentenceWords)
            
            for i in range(AllActualPreviousLyricTopSentenceWordsCount):
                Word = AllActualPreviousLyricTopSentenceWords[i].split(",")
                Word = Word[0].lower()
                LyricWords.append(Word)
                      
            WordsAppearence = {}
            AllWords = []
            for i in range(LyricsCount):
                OtherLyricWords = tokenize(Lyrics[i], StopWords)
                for p in range(len(OtherLyricWords)):
                    if OtherLyricWords[p] not in AllWords:
                        AllWords.append(OtherLyricWords[p])
                    
            for LyricWord in LyricWords:
                if LyricWord not in list(WordsAppearence.keys()):
                    WordsAppearence[LyricWord] = 0 
                for AllWord in AllWords:
                    if LyricWord == AllWord:
                        WordsAppearence[LyricWord] += 1  
                if WordsAppearence[LyricWord] > 1:
                    Quit = 1
            
            RepeatWords = {}
            for ActualPreviousLyricTopSentenceWord in ActualPreviousLyricTopSentenceWords:
                if "embed" in ActualPreviousLyricTopSentenceWord.lower():
                    Quit = 1
                if "lyric" in ActualPreviousLyricTopSentenceWord.lower():
                    Quit = 1
                RepeatWords[ActualPreviousLyricTopSentenceWord] = 0
                for LyricWord in LyricWords:
                    if LyricWord == ActualPreviousLyricTopSentenceWord:
                        RepeatWords[ActualPreviousLyricTopSentenceWord] += 1
                if RepeatWords[ActualPreviousLyricTopSentenceWord] > 3:
                    Quit = 1
            
            if Quit == 0:
                if PreviousLyricTopSentences[ActualPreviousLyricTopSentence] > 0:
                    PreviousWordsAppearence = 0
                    
                    for ActualPreviousLyricTopSentenceWord in ActualPreviousLyricTopSentenceWords:
                        for PreviousWord in PreviousWords:
                            if PreviousWord == ActualPreviousLyricTopSentenceWord:
                                PreviousWordsAppearence += 1 
                     
                    if LengthCount % 2 == 0:
                        if PreviousWordsAppearence != 2 :
                            Quit = 1
                    else:
                        if PreviousWordsAppearence != 1:
                            Quit = 1
                            
                    if Quit == 0:
                        
                        print(f'{PreviousLyric}')
                        print(f'{PreviousWords}')
                        print(f'{ActualPreviousLyricTopSentence}')
                        print(f'{ActualPreviousLyricTopSentenceWords}')
                        print(f'{LyricWords}')
                        print(f'{PreviousWordsAppearence}')
                        
                        PreviousLyric = ActualPreviousLyricTopSentence
                        Lyrics.append(PreviousLyric)
                        LyricsCount += 1
                        LengthCount += 1
                        break
                else:
                    PreviousWordsAppearence = 0
                    
                    print(f'{PreviousLyric}')
                    print(f'{PreviousWords}')
                    print(f'{ActualPreviousLyricTopSentence}')
                    print(f'{ActualPreviousLyricTopSentenceWords}')
                    print(f'{LyricWords}')
                    print(f'{PreviousWordsAppearence}')
                    
                    PreviousLyric = ActualPreviousLyricTopSentence
                    Lyrics.append(PreviousLyric)
                    LyricsCount += 1
                    LengthCount += 1
                    break
                        
    return Lyrics


def CalculateIDFs(AllFirstLineWords, SongPartsFirstLines):
    
    IDFs = {}
    SentenceCount = len(SongPartsFirstLines)
    
    Appearence = {}
    for FirstLineWord in AllFirstLineWords:
        Appearence[FirstLineWord] = 0
    
    Words = list(Appearence.keys())
    for Word in Words:
        for SongPartFirstLine in SongPartsFirstLines:
            Sentence = SongPartFirstLine.lower()
            if Word in Sentence:
                Appearence[Word] += 1
        AppearenceCount = Appearence[Word]
        if AppearenceCount > 0:
            IDF = math.log(SentenceCount/AppearenceCount)
            IDFs[Word] = IDF
        
    return IDFs


def TopSentences(ChorusWords, IDFs, SongPartsFirstLines, StopWords):
    
    SumIDFs = {}
    
    for SongPartsFirstLine in SongPartsFirstLines:
        SumOfIDFs = 0
        SongPartsFirstLineWords = SongPartsFirstLine.split(" ")
        for ChorusWord in ChorusWords:
            for SongPartsFirstLineWord in SongPartsFirstLineWords:
                Word = SongPartsFirstLineWord.split(",")
                ActualSongPartsFirstLineWord = Word[0].lower()
                if ActualSongPartsFirstLineWord == ChorusWord and ActualSongPartsFirstLineWord not in StopWords:
                    IDF = int(IDFs[ActualSongPartsFirstLineWord])
                    SumOfIDFs += IDF 
        SumIDFs[SongPartsFirstLine] = SumOfIDFs      
    TopSentences = {key: value for key, value in sorted(SumIDFs.items(), key = lambda element: element[1], reverse = True)}
    
    return TopSentences

if __name__ == "__main__":
    app.run()
    