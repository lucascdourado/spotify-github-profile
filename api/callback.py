from flask import Flask, Response, jsonify, render_template, redirect, request
from base64 import b64decode
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin

import os
import json
from util import spotify

print("Starting Server")

firebase_config = os.getenv('FIREBASE')
print(f"FIREBASE config: {firebase_config}")  # Para depuração
decoded_config = b64decode(firebase_config).decode('utf-8')
print(f"Decoded config: {decoded_config}")  # Para depuração
firebase_dict = json.loads(decoded_config)

cred = credentials.Certificate(firebase_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    try:
        code = request.args.get("code")
        if code is None:
            # TODO: no code
            return Response("not ok")

        token_info = spotify.generate_token(code)
        access_token = token_info["access_token"]

        spotify_user = spotify.get_user_profile(access_token)
        user_id = spotify_user["id"]

        doc_ref = db.collection("users").document(user_id)
        doc_ref.set(token_info)

        rendered_data = {
            "uid": user_id,
            "BASE_URL": spotify.BASE_URL,
        }

        return render_template("callback.html.j2", **rendered_data)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)
