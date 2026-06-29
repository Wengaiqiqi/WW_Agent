#!/usr/bin/env python3
"""修复 Dify 端口映射"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    hostname = "47.86.26.185"
    username = "root"
    password = "Ydmy5247."

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接到 {hostname}...")
        client.connect(hostname, 22, username, password, timeout=15, banner_timeout=30)
        print("[OK] SSH 连接成功")

        # 1. 更新 docker-compose.override.yaml
        print("\n--- 更新 docker-compose.override.yaml ---")
        override_content = '''version: "3.8"

services:
  web:
    ports:
      - "3001:3000"

  api:
    ports:
      - "5001:5001"

  nginx:
    deploy:
      replicas: 0
'''
        stdin, stdout, stderr = client.exec_command(
            f"cat > /opt/dify/docker/docker-compose.override.yaml << 'EOF'\n{override_content}EOF",
            timeout=10
        )
        print("docker-compose.override.yaml 已更新")

        # 2. 重启 Dify 服务
        print("\n--- 重启 Dify 服务 ---")
        stdin, stdout, stderr = client.exec_command(
            "cd /opt/dify/docker && docker compose down && docker compose up -d",
            timeout=120
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output[-500:] if len(output) > 500 else output)

        # 3. 等待容器启动
        print("\n--- 等待容器启动 ---")
        stdin, stdout, stderr = client.exec_command(
            "sleep 20",
            timeout=25
        )
        stdout.read()

        # 4. 检查容器状态
        print("\n--- 容器状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | head -15",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 测试 API
        print("\n--- 测试 API ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://localhost:5001/health --max-time 5 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 6. 测试 Web
        print("\n--- 测试 Web ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 --max-time 5",
            timeout=10
        )
        print(f"HTTP 状态码: {stdout.read().decode('utf-8', errors='ignore').strip()}")

        # 7. 测试外部访问
        print("\n--- 测试外部访问 ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s http://47.86.26.185:5001/health --max-time 5 2>&1",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
