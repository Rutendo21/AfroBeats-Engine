from flask import Flask, render_template, request
import csv

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

if __name__ == "__main__":
    app.run()
    