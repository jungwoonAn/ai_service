from flask import Flask, render_template, request
import sys 

app = Flask( __name__ )

@app.route( "/" )
def index():
    return "Hello, ChatGPT"

@app.route( "/chat-app" )
def chat_app():
    return render_template( "chat.html" )  

if __name__ == "__main__":
    app.run( host = '0.0.0.0', port = 8080, debug = True )
