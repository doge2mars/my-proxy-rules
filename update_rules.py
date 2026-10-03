import urllib.request
import re

# 1. 定义上游权威规则库地址 (blackmatrix7)
UPSTREAM_URLS = [
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/OpenAI/OpenAI.list",
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Claude/Claude.list",
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Gemini/Gemini.list",
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Copilot/Copilot.list",
]

def fetch_rules(url):
    print(f"正在拉取上游规则: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8').splitlines()
    except Exception as e:
        print(f"拉取失败 {url}: {e}")
        return []

all_rules = set()

# 2. 拉取各大上游规则
for url in UPSTREAM_URLS:
    lines = fetch_rules(url)
    for line in lines:
        line = line.strip()
        # 过滤注释与空行，保留纯规则行
        if line and not line.startswith('#') and not line.startswith('//'):
            all_rules.add(line)

# 3. 读取本地专属定制补丁 (custom_ai.list)
try:
    with open("custom_ai.list", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                all_rules.add(line)
except Exception as e:
    print(f"读取本地 custom_ai.list 提示: {e}")

# 4. 排序并清洗输出
sorted_rules = sorted(list(all_rules))

output_content = [
    "# ====================================================",
    "# 个人私有全能 AI 平台终极分流规则库 (自动同步合并版)",
    "# 数据源: blackmatrix7 (OpenAI + Claude + Gemini + Copilot) + 私人专属补丁",
    f"# 规则总条数: {len(sorted_rules)} 条",
    "# ====================================================",
    ""
] + sorted_rules

with open("AI.list", "w", encoding="utf-8") as f:
    f.write("\n".join(output_content) + "\n")

print(f"合并完成！共生成 {len(sorted_rules)} 条规则写入 AI.list")
