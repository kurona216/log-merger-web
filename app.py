from flask import Flask, request, send_file, render_template
from log_merger import merge_logs
import io
import os

app = Flask(__name__)

@app.route("/")
def index():
    # 使用 templates/index.html
    return render_template("index.html")

@app.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("files")
    if not files:
        return "没有上传文件", 400

    contents = [f.read().decode("utf-8", errors="ignore") for f in files]
    result = merge_logs(contents)

    return send_file(
        io.BytesIO(result.encode("utf-8")),
        as_attachment=True,
        download_name="合并结果.txt",
        mimetype="text/plain"
    )

if __name__ == "__main__":
    # Railway 必须用 PORT 环境变量
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
