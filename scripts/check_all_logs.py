#!/usr/bin/env python3
"""检查所有服务日志"""

import paramiko
import sys
import io
import time

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

        # 等待日志输出
        print("\n--- 等待 5 秒 ---")
        time.sleep(5)

        # 1. 检查服务状态
        print("\n--- 服务状态 ---")
        stdin, stdout, stderr = client.exec_command(
            "ps aux | grep -E 'hermes-gateway|hermes_a2a|gateway.*feishu' | grep -v grep",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 2. hermes-gateway 日志
        print("\n--- hermes-gateway 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -10 /tmp/hermes-gateway.log 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. hermes-a2a 日志
        print("\n--- hermes-a2a 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -10 /tmp/hermes-a2a.log 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 飞书 Gateway 日志
        print("\n--- 飞书 Gateway 日志 ---")
        stdin, stdout, stderr = client.exec_command(
            "tail -15 /root/feishu_gateway.log 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 测试 A2A
        print("\n--- 测试 A2A ---")
        stdin, stdout, stderr = client.exec_command(
            "curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8080/a2a --max-time 5",
            timeout=10
        )
        print(f"A2A 状态码: {stdout.read().decode('utf-8', errors='ignore').strip()}")

        # 6. 检查端口冲突
        print("\n--- 端口使用情况 ---")
        stdin, stdout, stderr = client.exec_command(
            "netstat -tlnp 2>/dev/null | grep -E ':3000|:3001|:5001|:5678|:8080' | sort",
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
