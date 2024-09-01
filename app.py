from flask import Flask, request, jsonify, send_from_directory, Response,render_template,send_file
import os  
import requests  
import threading  
import time  

static_ip = "172.31.19.161"
static_port = 5015

download_folder = "/home/ec2-user/workspace/upmodel/download"

# 设置你想要展示文件的目录
output_folder =  "/home/ec2-user/workspace/upmodel/download"
  
app = Flask(__name__)  
  
# 存储下载信息  
download_info = {}  
  
def download_file(url, path):  
    local_filename = url.split('/')[-1]  
    local_path = os.path.join(download_folder, path,local_filename)  
      
    # 模拟文件下载并发送进度  
    response = requests.get(url, stream=True)  
    total_size = int(response.headers.get('content-length', 0))  
    print(f"total size is {total_size/1024/1024}")
    downloaded = 0  
      
    with open(local_path, 'wb') as f:  
        for chunk in response.iter_content(chunk_size=8192):  
            if chunk:  
                f.write(chunk)  
                downloaded += len(chunk)  
                # 更新下载状态  
                download_info[url]['progress'] = int((downloaded / total_size) * 100)    
      
    download_info[url]['status'] = 'success'  
    download_info[url]['path'] = local_path  

@app.route('/models')
def models():
    # 渲染 HTML 模板
    return render_template('modelloads.html')

@app.route('/get_links')  
def get_links():  
    print("Client accessed URL:", request.url)
    parts = request.url.split("/")
    base_url = parts[2]
    links = [  
        {"name": "ComfyUI绘图", "url": "https://www.baidu.com"},  
        {"name": "模型管理", "url": f"http://{base_url}/models"},  
        {"name": "图片输出", "url": f"http://{base_url}/output"}  
    ]  
    return jsonify(links) 

@app.route('/')
def index():
    # 渲染 HTML 模板
    return render_template('index.html')


@app.route('/download', methods=['POST'])  
def start_download():  
    url = request.json['url']  
    path = request.json['path']  
      
    # 初始化下载信息  
    download_info[url] = {'status': 'downloading', 'progress': 0, 'path': None}  
      
    # 开启线程进行下载  
    threading.Thread(target=download_file, args=(url, path)).start()  
      
    return jsonify({'status': 'downloading'})  
  
@app.route('/status/<path:url>')  
def get_status(url):  
    return jsonify(download_info.get(url, {'status': 'not found'}))  


@app.route('/output')
def output():
    files_info = []
    for f in os.listdir(output_folder):
        filepath = os.path.join(output_folder, f)
        if os.path.isfile(filepath):
            # 获取文件的创建时间
            creation_time = os.path.getctime(filepath)
            # 转换为可读的格式
            readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_time))
            files_info.append({'name': f, 'creation_time': readable_time})
    files_info.sort(key=lambda x: x['creation_time'], reverse=True)  # 可选：按创建时间排序
    return render_template('output.html', files=files_info)

@app.route('/output_download/<filename>')
def output_download(filename):
    # 从指定目录发送文件进行下载
    file_path = output_folder + "/" + filename
    return send_file(file_path, as_attachment=True)

  
if __name__ == '__main__':
    app.run(port=5015, host=static_ip)