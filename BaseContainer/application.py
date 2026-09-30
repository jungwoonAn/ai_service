from flask import Flask, render_template, request
import sys 

application = Flask( __name__ )

@application.route( "/" )
def index():
    return "Hello, ChatGPT"

@application.route( "/chat-app" )
def chat_app():
    return render_template( "chat.html" )  

if __name__ == "__main__":
    application.run( host = '0.0.0.0', port = 8080, debug = True )
