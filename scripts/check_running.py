#!/usr/bin/env python3
"""检查服务器上实际运行的服务"""

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

        # 1. 所有 Python 进程
        print("\n--- Python 进程 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep python | grep -v grep",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. Docker 容器
        print("\n--- Docker 容器 ---")
        stdin, stdout, stderr = client.exec_command(
            "docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 监听端口
        print("\n--- 监听端口 ---")
        stdin, stdout, stderr = client.exec_command(
            "netstat -tlnp 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 检查关键服务
        print("\n--- 关键服务检查 ---")
        services = [
            ("hermes-gateway", "ps aux | grep 'hermes-gateway' | grep -v grep"),
            ("A2A 桥接", "ps aux | grep 'hermes_a2a' | grep -v grep"),
            ("飞书 Gateway", "ps aux | grep 'gateway.*feishu' | grep -v grep"),
            ("uvicorn 8080", "netstat -tlnp | grep :8080"),
        ]

        for name, cmd in services:
            stdin, stdout, stderr = client.exec_command(cmd, timeout=5)
            output = stdout.read().decode('utf-8', errors='ignore').strip()
            status = "✅ 运行中" if output else "❌ 未运行"
            print(f"  {name}: {status}")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
