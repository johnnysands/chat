from bandolier import Bandolier, annotate_arguments, annotate_description
from flask import Flask, render_template, request, url_for, session
from flask_session import Session
import uuid


app = Flask(__name__)

# Flask session configuration
with open("secret_key.txt", "r") as file:
    secret_key = file.read().replace("\n", "")
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def chat():
    if "chats" not in session:
        session["chats"] = {}
        # TODO using the active chat in the session means accessing the chat
        # from two tabs simultaneously might exhibit broken behavior.
        session["active_chat"] = str(uuid.uuid4())
        session["chats"][session["active_chat"]] = []
        session["chat_titles"] = {}
        session.modified = True

    chats = {}
    chat_titles = session.get("chat_titles", {})  # TODO removeme after migration
    for chat_id in session["chats"].keys():
        title = chat_titles.get(chat_id, "Buggy chat")
        chats[chat_id] = title
    # TODO chat titles should be sorted by last activity

    return render_template(
        "chat.html",
        active_chat=session["active_chat"],
        chats=chats,
    )


@app.route("/new-chat", methods=["POST"])
def new_chat():
    # new chat creates a new active chat id.
    session["active_chat"] = str(uuid.uuid4())
    session["chats"][session["active_chat"]] = []
    session["chat_titles"][session["active_chat"]] = "New chat"
    session.modified = True
    return "", 204


@app.route("/retrieve-chat/<chat_id>", methods=["GET"])
def retrieve_chat(chat_id):
    messages = []

    if chat_id not in session["chats"]:
        session["chats"][chat_id] = []

    for m in session["chats"][chat_id]:
        # filter out function calls
        if m.content is None:
            continue
        # filter out all other roles
        if m["role"] == "assistant" or m["role"] == "user":
            messages.append(m)
    session["active_chat"] = chat_id
    session.modified = True
    return render_template("chat_messages.html", messages=messages)


@app.route("/delete-chat", methods=["POST"])
def delete_chat():
    # delete the chat id in the form
    chat_id = request.form.get("chat_id")

    if chat_id == session["active_chat"]:
        session["active_chat"] = uuid.uuid4()
        session["chats"][session["active_chat"]] = []

    del session["chats"][chat_id]

    session.modified = True
    return "", 204


@app.route("/send-message", methods=["POST"])
def send_message():
    # get chat_id from form
    chat_id = request.form.get("chat_id")

    # load bandolier with stored state
    bandolier = Bandolier()
    bandolier.messages = session["chats"][chat_id]
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
