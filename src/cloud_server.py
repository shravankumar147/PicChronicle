from flask import Flask, request, send_from_directory, jsonify
import os

UPLOAD_FOLDER = r"C:\Users\shravan\Documents\Python_Scripts\PicChronicle\data\unorganized\CloudStorage"  # Change this to your 2TB hard drive path
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Route for uploading files
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
    return jsonify({"message": "File uploaded successfully!"}), 200

# Route for listing files
@app.route("/files", methods=["GET"])
def list_files():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return jsonify({"files": files})

# Route for downloading files
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # app.run(host="0.0.0.0", port=443, ssl_context=("cert.pem", "key.pem"))
