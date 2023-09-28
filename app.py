from flask import Flask
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect('database.db')

@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)