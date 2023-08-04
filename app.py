from flask import Flask, render_template, request, url_for, session
from bandolier import Bandolier
from flask_session import Session  # you need to install this module


app = Flask(__name__)

# Flask session configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "889cee86add812714b96fa96c57ea31024157ad21ced3bc56292c61d"
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
