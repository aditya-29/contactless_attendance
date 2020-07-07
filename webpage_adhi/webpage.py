import os
from flask import Flask, request, render_template
import utils as u

app = Flask(__name__)


@app.route("/")

def main():
    return render_template("index.html")
database = {"adhi" : "adhi", "jb":"jb"}

@app.route("/form_login", methods = ["POST", "GET"])

def login():
    name = request.form["username"]
    pwd = request.form["password"]

    if name not in database:
        return render_template("index.html", info="invalid user")

    else:
        if database[name] != pwd:
            return render_template("index.html", info="password incorrect")

        else:
            return render_template("stream.html")


if __name__ == "__main__":
    app.run()


main()
