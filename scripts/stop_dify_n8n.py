#!/usr/bin/env python3
"""停止 Dify 和 n8n 服务"""

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
        client.connect(hostname, 22, username, password, timeout=20, banner_timeout=30)
        print("[OK] SSH 连接成功")

        # 1. 停止 Dify
        print("\n--- 停止 Dify ---")
        stdin, stdout, stderr = client.exec_command(
            "cd /opt/dify/docker && docker compose down",
            timeout=60
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output[-300:] if len(output) > 300 else output)

        # 2. 停止 n8n
        print("\n--- 停止 n8n ---")
        stdin, stdout, stderr = client.exec_command(
            "docker stop n8n 2>/dev/null && docker rm n8n 2>/dev/null || echo 'n8n 容器不存在'",
            timeout=30
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "n8n 已停止")

        # 3. 检查剩余容器
        print("\n--- 剩余容器 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 检查端口
        print("\n--- 端口使用 ---")
        stdin, stdout, stderr = client.exec_command(
            "netstat -tlnp 2>/dev/null | grep -E ':3001|:5001|:5003|:5678' || echo '端口已释放'",
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
