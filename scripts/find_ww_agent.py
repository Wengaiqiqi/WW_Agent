#!/usr/bin/env python3
"""在服务器上查找 W&W Agent"""

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

        # 1. 查找 W&W Agent
        print("\n--- 查找 W&W Agent ---")
        stdin, stdout, stderr = client.exec_command(
            "find / -maxdepth 4 -type d -name '*ww*' -o -name '*W&W*' -o -name '*ww-agent*' 2>/dev/null | head -10",
            timeout=15
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "未找到")

        # 2. 查找 agent 相关目录
        print("\n--- 查找 agent 目录 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /opt/ 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 3. 查找 home 目录
        print("\n--- home 目录 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /root/ 2>/dev/null | head -20",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 4. 查找 .hermes-a2a 目录
        print("\n--- .hermes-a2a 目录 ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /root/.hermes-a2a/ 2>/dev/null",
            timeout=10
        )
        print(stdout.read().decode('utf-8', errors='ignore').strip())

        # 5. 查找 cli.py 或 web 相关文件
        print("\n--- 查找 cli.py ---")
        stdin, stdout, stderr = client.exec_command(
            "find /root -name 'cli.py' -o -name 'web' -type d 2>/dev/null | head -10",
            timeout=10
        )
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        print(output if output else "未找到")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
