import websocket
import uuid
import json
import urllib.request
import urllib.parse
import os
from pathlib import Path
import time
import random

class ComfyUIGenerator:
    def __init__(self, host="127.0.0.1", port="8188"):
        self.server_address = f"{host}:{port}"
        self.client_id = str(uuid.uuid4())
        self.output_dir = Path("output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载工作流配置
        try:
            with open("Base.json", "r", encoding="utf-8") as f:
                self.workflow = json.load(f)
                print("成功加载工作流配置")
        except Exception as e:
            print(f"加载工作流配置失败: {e}")
            raise

    def queue_prompt(self, prompt):
        """发送提示词到队列"""
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(self, filename, subfolder, folder_type):
        """获取生成的图片"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()

    def get_history(self, prompt_id):
        """获取生成历史"""
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())

    def get_images(self, ws, workflow, output_file):
        """获取生成的图片并保存"""
        try:
            # 打印工作流配置（调试用）
            print("\n工作流配置:")
            for node_id, node in workflow.items():
                if node["class_type"] == "CLIPTextEncode":
                    print(f"节点 {node_id}: {node['inputs']['text']}")
            
            # 发送提示词到队列
            prompt_id = self.queue_prompt(workflow)['prompt_id']
            print(f"提示词已发送，等待生成...")

            # 等待生成完成
            while True:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        data = message['data']
                        if data['node'] is None and data['prompt_id'] == prompt_id:
                            break
                else:
                    continue

            # 获取生成结果
            history = self.get_history(prompt_id)[prompt_id]
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    for image in node_output['images']:
                        image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                        # 保存图片
                        with open(output_file, 'wb') as f:
                            f.write(image_data)
                        print(f"图片已保存: {output_file}")
                        return True

            return False
        except Exception as e:
            print(f"生成图片时出错: {e}")
            print(f"工作流数据: {json.dumps(workflow, indent=2)}")
            raise

    def generate_images(self, key_scenes_file: str):
        """为所有场景生成图片"""
        # 读取场景信息
        with open(key_scenes_file, "r", encoding="utf-8") as f:
            scenes = json.load(f)
        
        print(f"找到 {len(scenes)} 个场景需要生成图片")
        
        # 连接 WebSocket
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
        
        try:
            for scene in scenes:
                print(f"\n生成场景 {scene['scene_id']} 的图片...")
                print(f"提示词: {scene['prompt']}")
                
                # 准备输出文件名
                output_file = self.output_dir / scene['image_file']
                if output_file.exists():
                    print(f"图片已存在: {output_file}")
                    continue
                
                # 创建工作流的深拷贝
                workflow = json.loads(json.dumps(self.workflow))
                
                # 设置随机种子和更新提示词
                seed = random.randint(1, 9999999999)
                positive_prompt = scene["prompt"] + ", masterpiece, best quality, photorealistic, cinematic lighting, movie style, detailed, 8k uhd"
                negative_prompt = "text, watermark, bad quality, worst quality, low quality, illustration, 3d render, cartoon, anime, manga"
                
                # 更新工作流配置
                workflow["3"]["inputs"]["seed"] = seed  # KSampler 节点
                workflow["6"]["inputs"]["text"] = positive_prompt  # 正面提示词节点
                workflow["7"]["inputs"]["text"] = negative_prompt  # 负面提示词节点
                
                print(f"设置随机种子: {seed}")
                print(f"设置正面提示词: {positive_prompt}")
                print(f"设置负面提示词: {negative_prompt}")
                
                try:
                    success = self.get_images(ws, workflow, output_file)
                    if not success:
                        print("图片生成失败")
                except Exception as e:
                    print(f"生成图片时出错: {e}")
                
                # 等待一小段时间再生成下一张
                time.sleep(1)
        
        finally:
            ws.close()

if __name__ == "__main__":
    generator = ComfyUIGenerator()
    generator.generate_images("output/key_scenes.json") 