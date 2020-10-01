from flask import Flask, jsonify, request

from rockimage import config

app = Flask(__name__)


@app.route("/")
def root():
    return jsonify({"message": "Hello Cloud - testing build... "}), 200


if config.ENABLE_API:
    from rockimage import service

    @app.route("/images", methods=["GET"])
    def list_images():
        images = service.list_images()
        return jsonify(images), 200

    @app.route("/images/", methods=["POST"])
    def create_image():
        image = request.files['file']
        result = service.save_image(image)
        return jsonify(result), 200

    @app.route("/images/<uuid:uuid>")
    def get_image(uuid: str):
        print("Got through inital get_image method...")
        print(uuid)
        image = service.get_image(uuid)
        return jsonify(image), 200
