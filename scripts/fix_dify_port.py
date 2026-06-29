#!/usr/bin/env python3
"""修改 Dify 端口配置"""

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

        # 1. 检查当前 docker-compose.override.yaml
        print("\n--- 当前 docker-compose.override.yaml ---")
        stdin, stdout, stderr = client.exec_command(
            "cat /opt/dify/docker/docker-compose.override.yaml 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. 修改 .env 文件中的端口配置
        print("\n--- 修改 .env 端口配置 ---")
        # 将 Web 端口从 3000 改为 3001
        stdin, stdout, stderr = client.exec_command(
            "sed -i 's/DIFY_PORT=5001/DIFY_PORT=5001/' /opt/dify/docker/.env",
            timeout=10
        )
        print("DIFY_PORT 保持 5001")

        # 3. 创建/修改 docker-compose.override.yaml 来覆盖端口
        print("\n--- 创建 docker-compose.override.yaml ---")
        override_content = """version: '3'
services:
  web:
    ports:
      - "3001:3000"
"""
        # 写入文件
        stdin, stdout, stderr = client.exec_command(
            f"cat > /opt/dify/docker/docker-compose.override.yaml << 'EOF'\n{override_content}EOF",
            timeout=10
        )
        print("docker-compose.override.yaml 已更新")

        # 4. 重启 Dify 服务
        print("\n--- 重启 Dify 服务 ---")
        stdin, stdout, stderr = client.exec_command(
            "cd /opt/dify/docker && docker compose down && docker compose up -d",
            timeout=60
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        error = stderr.read().decode('utf-8', errors='ignore').strip()
        if output:
            print(output[-500:] if len(output) > 500 else output)
        if error:
            print(f"STDERR: {error[-500:] if len(error) > 500 else error}")

        # 5. 检查新的端口
        print("\n--- 检查新端口 ---")
        stdin, stdout, stderr = client.exec_command(
            "netstat -tlnp | grep -E '3000|3001|5001' 2>/dev/null",
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
