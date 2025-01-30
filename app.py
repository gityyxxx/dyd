from flask import Flask, render_template, request, session, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from config import USERNAME, PASSWORD, DEFAULT_SAVE_DIR
import subprocess
import os
import threading

app = Flask(__name__)
app.secret_key = "supersecretkey"  # 设置会话密钥
auth = HTTPBasicAuth()

# 简单密码验证（或使用 session 验证）
users = {
    USERNAME: generate_password_hash(PASSWORD)
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# 确保下载目录存在
if not os.path.exists(DEFAULT_SAVE_DIR):
    os.makedirs(DEFAULT_SAVE_DIR)

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html', save_dir=DEFAULT_SAVE_DIR)

@app.route('/download', methods=['POST'])
@auth.login_required
def download():
    url = request.form['url']
    save_dir = request.form.get('save_dir', DEFAULT_SAVE_DIR)
    
    # 防止路径遍历攻击
    if not os.path.abspath(save_dir).startswith(DEFAULT_SAVE_DIR):
        return "Invalid directory!", 400

    # 启动后台下载线程
    threading.Thread(target=run_download, args=(url, save_dir)).start()
    
    return "Download started! Check the download directory later."

def run_download(url, save_dir):
    # 抖音直播可能需要附加参数（如 --live-from-start）
    command = [
        'youtube-dl',
        url,
        '-o', f'{save_dir}/%(title)s-%(id)s.%(ext)s',
        '--live-from-start'  # 确保从直播开始录制
    ]
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Download failed: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
