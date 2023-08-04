from bandolier import Bandolier, annotate_arguments, annotate_description
from flask import Flask, render_template, request, url_for, session
from flask_session import Session


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

    messages = []
    for m in session["messages"]:
        # filter out function calls
        if m.content is None:
            continue
        # filter out all other roles
        if m["role"] == "assistant" or m["role"] == "user":
            messages.append(m)
    return render_template("chat.html", messages=messages)


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
    bandolier.add_function(get_weather)

    # process the incoming message
    message = request.form.get("message")
    bandolier.add_user_message(message)
    response = bandolier.run()

    # send the response
    session["messages"] = bandolier.messages
    session.modified = True
    return f'<div class="chat-message server-message"><span class="username">{response.role}:</span> {response.content}</div>'


@annotate_arguments(
    {
        "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA.",
        },
        "unit": {
            "type": "string",
            "description": "The unit to return the temperature in, e.g. F or C.",
            "default": "F",
        },
    }
)
@annotate_description("Get the weather for a location.")
def get_weather(location, unit="F"):
    return {"temperature": 72, unit: unit, "conditions": ["sunny", "windy"]}


def load_bandolier():
    bandolier = Bandolier()
    bandolier.add_function(get_weather)
    return bandolier


if __name__ == "__main__":
    app.run(debug=True)
