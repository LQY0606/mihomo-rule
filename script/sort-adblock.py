import os
import sys
import re

# 定义需要过滤的国家域名后缀
REMOVE_TLD = {
    # 亚洲
    ".jp", ".kr", ".in", ".id", ".th", ".sg", ".my", ".ph", ".vn",
    ".pk", ".bd", ".lk", ".np", ".mn", ".uz", ".kz", ".kg", ".bt", ".mv", ".mm",

    # 欧洲
    ".uk", ".de", ".fr", ".it", ".es", ".ru", ".nl", ".be", ".ch", ".at", ".pl",
    ".cz", ".se", ".no", ".fi", ".dk", ".gr", ".pt", ".ie", ".hu", ".ro", ".bg",
    ".sk", ".si", ".lt", ".lv", ".ee", ".is", ".md", ".ua", ".by", ".am", ".ge",

    # 美洲
    ".us", ".ca", ".mx", ".br", ".ar", ".cl", ".co", ".pe", ".ve", ".uy", ".py",
    ".bo", ".ec", ".cr", ".pa", ".do", ".gt", ".sv", ".hn", ".ni", ".jm", ".cu",

    # 非洲
    ".za", ".eg", ".ng", ".ke", ".gh", ".tz", ".ug", ".dz", ".ma", ".tn", ".ly",
    ".ci", ".sn", ".zm", ".zw", ".ao", ".mz", ".bw", ".na", ".rw", ".mw", ".sd",

    # 大洋洲
    ".au", ".nz", ".fj", ".pg", ".sb", ".vu", ".nc", ".pf", ".ws", ".to", ".ki",
    ".tv", ".nr", ".as",

    # 中东
    ".sa", ".ae", ".ir", ".il", ".iq", ".tr", ".sy", ".jo", ".lb", ".om", ".qa",
    ".ye", ".kw", ".bh"
}

def extract_domain(rule):
    """从 Adblock 规则中提取域名"""
    match = re.match(r'\|\|([a-zA-Z0-9.-]+)', rule)
    return match.group(1) if match else None

def get_parent_domain(domain):
    """获取父域名"""
    parts = domain.split('.')
    if len(parts) > 2:
        return '.'.join(parts[-2:])
    return domain

def has_removable_tld(domain):
    """检查域名是否以指定后缀结尾"""
    return any(domain.endswith(tld) for tld in REMOVE_TLD)

# 读取输入文件名
file_name = sys.argv[1]

# 打开文件并读取所有行
with open(file_name, 'r', encoding='utf8') as f:
    lines = f.readlines()

# 提取域名规则
domains = set()
for line in lines:
    line = line.strip()
    if line.startswith('||'):  # 只处理 || 开头的规则
        domain = extract_domain(line)
        if domain:
            domains.add(domain)

# 去除子域名，保留父域名
parent_domains = set()
subdomains = set()

for domain in domains:
    parent_domain = get_parent_domain(domain)
    if parent_domain in parent_domains or domain == parent_domain:
        # 如果父域名已存在，或者当前域名本身是父域名
        continue
    if domain != parent_domain:
        # 如果是子域名，暂存到子域名集合
        subdomains.add(domain)
    else:
        # 否则添加到父域名集合
        parent_domains.add(parent_domain)

# 从父域名集合中移除与子域名冲突的
for subdomain in subdomains:
    parent_domain = get_parent_domain(subdomain)
    if parent_domain in parent_domains:
        # 存在子域名时，保留父域名，移除子域名
        domains.discard(subdomain)

# 去除以指定后缀结尾的域名
filtered_domains = {domain for domain in domains if not has_removable_tld(domain)}

# 排序规则：先按父域名排序，再按子域名排序
sorted_domains = sorted(filtered_domains, key=lambda d: (get_parent_domain(d), d))

# 转换为 domain 格式
domain_rules = [f"{domain}\n" for domain in sorted_domains]

# 写入文件
with open(file_name, 'w', encoding='utf8') as f:
    f.writelines(domain_rules)

print(f"处理完成，生成的规则总数为：{len(domain_rules)}")
