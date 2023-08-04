from flask import Flask, render_template, request, url_for
import bandolier

bandolier = bandolier.Bandolier()
bandolier.add_system_message("You are a helpful assistant.")

app = Flask(__name__)


@app.route("/")
def chat():
    return render_template("chat.html")


@app.route("/send-message", methods=["POST"])
def send_message():
    message = request.form.get("message")
    bandolier.add_user_message(message)
    response = bandolier.run()
    return f'<div class="chat-message server-message"><span class="username">{response.role}</span>{response.content}</div>'


if __name__ == "__main__":
    app.run(debug=True)
