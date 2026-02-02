from flask import Flask, request, send_file, render_template_string
from log_merger import merge_logs
import io

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>跑团日志合并</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f4f5f7;
    margin: 0;
    padding: 0;
  }
  .container {
    max-width: 520px;
    margin: 60px auto;
    background: #ffffff;
    padding: 32px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  }
  h1 {
    margin-top: 0;
    font-size: 22px;
    text-align: center;
  }
  p {
    color: #666;
    font-size: 14px;
    text-align: center;
    margin-bottom: 24px;
  }
  input[type=file] {
    width: 100%;
    margin-bottom: 20px;
  }
  button {
    width: 100%;
    background: #4f46e5;
    color: #fff;
    border: none;
    padding: 12px;
    font-size: 16px;
    border-radius: 8px;
    cursor: pointer;
  }
  button:hover {
    background: #4338ca;
  }
  footer {
    margin-top: 24px;
    text-align: center;
    font-size: 12px;
    color: #aaa;
  }
</style>
</head>
<body>

<div class="container">
  <h1>跑团日志合并工具</h1>
  <p>上传多个 QQ 跑团日志（.txt），自动合并、排序并替换图片</p>

  <form action="/merge" method="post" enctype="multipart/form-data">
    <input type="file" name="files" multiple accept=".txt">
    <button type="submit">开始合并</button>
  </form>

  <footer>
    本工具仅在本地/服务器处理，不会保存你的文件
  </footer>
</div>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("files")
    contents = [f.read().decode("utf-8", errors="ignore") for f in files]

    result = merge_logs(contents)

    return send_file(
        io.BytesIO(result.encode("utf-8")),
        as_attachment=True,
        download_name="合并结果.txt",
        mimetype="text/plain"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
