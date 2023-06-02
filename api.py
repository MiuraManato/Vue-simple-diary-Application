from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import datetime

app = Flask(__name__)
CORS(app)

# アップロードされたファイルを保存するディレクトリ
# 実行環境に左右されないようにする
user_path = os.getcwd()
app.config["UPLOAD_FOLDER"] = user_path + r"\uploads"

# 投稿データを保存するファイル
posts_file = "posts.json"

# POSTメソッドで投稿されたデータの処理
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files: file = None
    else:
        file = request.files["file"]
        if file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    # タイトル、コンテンツが入力されていなかった場合にエラーを返す
    if "title" not in request.form: return ("Missing title", 400)
    if "content" not in request.form: return ("Missing content", 400)

    title = request.form["title"]
    content = request.form["content"]
    date = datetime.datetime.now().strftime("%Y %m/%d %H:%M")

    try:
        with open(posts_file, "r") as f:
            posts = json.load(f)
    except:
        posts = []

    post = {"id": len(posts)+1, "title": title, "content": content, "date": date, "file": user_path + r'/uploads/' + filename if file else None}

    posts.append(post)

    with open(posts_file, "w") as f:
        json.dump(posts, f)

    return ("Post created successfully", 200)

@app.route("/getPosts", methods=["GET"])
def get_posts():
    # ファイルの内容がない場合には空のリストを返す
    try:
        with open(posts_file, "r") as f:
            posts = json.load(f)
        return jsonify(posts)
    except:
        return jsonify([])

@app.route("/getPost/<int:post_id>", methods=["GET"])
def get_post(post_id):
    try:
        with open(posts_file, "r") as f:
            posts = json.load(f)
        post = next((post for post in posts if post['id'] == post_id), None)
        if post:
            return jsonify(post)
        else:
            return jsonify({"message": "Post not found"}), 404
    except:
        return jsonify({"message": "Internal Server Error"}), 500


@app.errorhandler(500)
def handle_cors_error(e):
    return jsonify({"message": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
