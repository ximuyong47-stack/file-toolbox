import os, tempfile, subprocess, uuid, shutil
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

ALLOWED_EXTENSIONS = {"docx", "xlsx", "doc", "xls"}
LIBREOFFICE = os.environ.get("LIBREOFFICE_PATH", "libreoffice")

@app.route("/")
def index():
    return jsonify({"status": "ok", "service": "文档格式编辑器 - PDF转换服务"})

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "请上传文件"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "文件名为空"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"不支持的文件格式：.{ext}"}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        input_name = secure_filename(file.filename)
        input_path = os.path.join(temp_dir, input_name)
        file.save(input_path)

        result = subprocess.run(
            [LIBREOFFICE, "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_path],
            capture_output=True, text=True, timeout=60
        )

        pdf_name = input_name.rsplit(".", 1)[0] + ".pdf"
        pdf_path = os.path.join(temp_dir, pdf_name)

        if not os.path.exists(pdf_path):
            return jsonify({"error": "转换失败", "detail": result.stderr[:500]}), 500

        return send_file(pdf_path, mimetype="application/pdf",
                         as_attachment=True,
                         download_name=pdf_name)

    except subprocess.TimeoutExpired:
        return jsonify({"error": "转换超时"}), 500
    except Exception as e:
        return jsonify({"error": f"服务异常：{str(e)}"}), 500
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
