from flask import Flask, Blueprint
from flask_cors import CORS
from routes.graph_routes import graph_routes
from routes.test_routes import test_routes
from routes.entities_routes import entities_routes
from routes.create_routes import create_routes
from routes.doc_routes import doc_routes

app = Flask(__name__)
app.json.sort_keys = False

CORS(app)

app.config["CORS_HEADERS"] = "Content-Type"

# Register the Blueprint
app.register_blueprint(graph_routes)
app.register_blueprint(test_routes)
app.register_blueprint(entities_routes)
app.register_blueprint(create_routes)
app.register_blueprint(doc_routes)

if __name__ == "__main__":
    app.run(debug=True)
