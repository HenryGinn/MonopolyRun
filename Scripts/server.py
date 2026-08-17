import os

from flask import Flask, send_from_directory, jsonify
import networkx as nx
import osmnx as ox


class Server():
    
    def __init__(self, monopoly):
        self.monopoly = monopoly
        self.app = Flask(__name__)
        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule("/", "home", self.home)
        self.app.add_url_rule("/<path:file>", "files", self.files)
        self.app.add_url_rule("/style.json", "style", lambda: jsonify(self.monopoly.style))

    def home(self):
        return send_from_directory(self.monopoly.source_path, "index.html")

    def files(self, file):
        return send_from_directory(
            self.monopoly.source_path,
            file,
            mimetype="text/javascript" if file.endswith(".mjs") else None)

    def run(self):
        self.app.run(
            host="127.0.0.1",
            port=8000)
