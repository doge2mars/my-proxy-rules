#!/usr/bin/env python3
import sys
import os
import shutil
import urllib.request
import ssl
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 1. 基础路径安全设置（绝对路径，避免 cron/不同工作目录报错）
BASE_DIR = Path(__file__).resolve().parent
CUSTOM_FILE = BASE_DIR / "custom_ai.list"
OUTPUT_FILE = BASE_DIR / "AI.list"
BACKUP_FILE = BASE_DIR / "AI.list.bak"
TEMP_FILE = BASE_DIR / "AI.list.tmp"

# 2. 上游权威规则库地址 (blackmatrix7)
UPSTREAM_SOURCES = {
    "OpenAI": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/OpenAI/OpenAI.list",
    "Claude": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Claude/Claude.list",
    "Gemini": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Gemini/Gemini.list",
    "Copilot": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Copilot/Copilot.list",
}

VALID_PREFIXES = (
    "DOMAIN,", "DOMAIN-SUFFIX,", "DOMAIN-KEYWORD,",
    "IP-CIDR,", "IP-CIDR6,", "IP-ASN,", "PROCESS-NAME,"
)

def fetch_rules(name, url):
    print(f"[*] 正在拉取上游规则 [{name}]: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        # 默认启用标准 SSL 证书校验，防止中间人劫持；如果遇到缺少本地根证书的环境则自适应降级重试
        try:
            resp_ctx = urllib.request.urlopen(req, timeout=20)
        except ssl.SSLCertVerificationError:
            print(f"    [!] 警告: 本地未安装系统根证书，临时降级重试拉取 [{name}]...")
            unverified_ctx = ssl._create_unverified_context()
            resp_ctx = urllib.request.urlopen(req, context=unverified_ctx, timeout=20)

        with resp_ctx as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP 状态码异常: {resp.status}")
            lines = resp.read().decode('utf-8').splitlines()
            valid_lines = [
                line.strip() for line in lines
                if line.strip() and not line.strip().startswith(('#', '//'))
            ]
            if len(valid_lines) == 0:
                raise ValueError(f"上游 [{name}] 返回规则数为 0，可能源已失效或被拦截")
            print(f"    -> 成功获取 {len(valid_lines)} 条规则")
            return valid_lines
    except Exception as e:
        print(f"[!] 严重错误: 拉取 [{name}] 失败: {e}", file=sys.stderr)
        # 坚决拒绝静默失败，抛出异常阻断运行，防止破坏已有的 AI.list
        raise

def load_custom_rules(file_path):
    print(f"[*] 正在读取本地私人定制规则: {file_path}")
    if not file_path.exists():
        raise FileNotFoundError(f"本地补丁文件不存在: {file_path}")
    valid_lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()
            # 严格过滤注释和空行（支持 # 和 //）
            if clean and not clean.startswith(('#', '//')):
                valid_lines.append(clean)
    print(f"    -> 本地定制规则共 {len(valid_lines)} 条")
    return valid_lines

def main():
    source_stats = {}
    all_rules = set()

    # 1. 拉取所有上游，任一失败立即退出，保护旧文件
    for name, url in UPSTREAM_SOURCES.items():
        try:
            rules = fetch_rules(name, url)
            source_stats[name] = len(rules)
            all_rules.update(rules)
        except Exception as e:
            print(f"[x] 管线终止: 上游数据源 [{name}] 异常，放弃更新以保护生产文件！", file=sys.stderr)
            sys.exit(1)

    # 2. 读取本地定制规则
    try:
        custom_rules = load_custom_rules(CUSTOM_FILE)
        source_stats["Custom (私人补丁)"] = len(custom_rules)
        all_rules.update(custom_rules)
    except Exception as e:
        print(f"[x] 管线终止: 读取本地定制规则失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. 轻量校验合法性，剔除未知格式
    valid_rules = []
    for r in all_rules:
        if any(r.startswith(p) for p in VALID_PREFIXES):
            valid_rules.append(r)
        else:
            print(f"[?] 警告: 跳过未知格式规则: {r}")

    sorted_rules = sorted(valid_rules)

    # 4. 组装头部元数据与明细
    bj_time = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S (UTC+8)")
    header = [
        "# ==================================================================",
        "# 个人私有全能 AI 平台终极分流规则库 (自动化原子构建版)",
        f"# 构建时间: {bj_time}",
        f"# 规则总条数: {len(sorted_rules)} 条",
        "# 数据源统计明细:",
    ]
    for src, cnt in source_stats.items():
        header.append(f"#   - {src:20s}: {cnt} 条")
    header.append("# ==================================================================")
    header.append("")

    full_content = "\n".join(header + sorted_rules) + "\n"

    # 5. 写入前备份旧版本 + 原子替换
    try:
        # A. 如果已存在旧文件，先保留一份 .bak，方便一键回滚
        if OUTPUT_FILE.exists():
            shutil.copy2(OUTPUT_FILE, BACKUP_FILE)
            print(f"[*] 已安全备份当前版本至: {BACKUP_FILE.name}")

        # B. 先写临时文件
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        # C. 原子重命名替换
        os.replace(TEMP_FILE, OUTPUT_FILE)
        print(f"[+] 更新大功告成！全量 {len(sorted_rules)} 条清洗规则已安全写入 {OUTPUT_FILE.name}")
    except Exception as e:
        if TEMP_FILE.exists():
            TEMP_FILE.unlink()
        print(f"[x] 写入目标文件失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
