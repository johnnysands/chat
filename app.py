from bandolier import Bandolier
from flask import Flask, render_template, request, url_for, session
from flask_session import Session  # you need to install this module
import os


app = Flask(__name__)

# Flask session configuration
with open("secret_key.txt", "r") as file:
    secret_key = file.read().replace("\n", "")
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def chat():
    if "messages" not in session:
        session["messages"] = []
    return render_template("chat.html", messages=session["messages"])


@app.route("/new-chat", methods=["POST"])
def new_chat():
    # Clear the chat messages from the session
    session["messages"] = []
    session.modified = True
    return "", 204


@app.route("/send-message", methods=["POST"])
def send_message():
    # initialize bandolier with stored state
    bandolier = Bandolier()
    bandolier.messages = session["messages"]

    # process the incoming message
    message = request.form.get("message")
    bandolier.add_user_message(message)
    response = bandolier.run()

    # send the response
    session["messages"] = bandolier.messages
    session.modified = True
    return f'<div class="chat-message server-message"><span class="username">{response.role}:</span> {response.content}</div>'


if __name__ == "__main__":
    app.run(debug=True)
