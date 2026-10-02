import pandas as pd
import requests
import time
import json

# 读取核心靶点
targets = pd.read_csv("data/ad_core_targets.csv")
symbols = targets["symbol"].tolist()
print(f"待查询靶点：{len(symbols)} 个")

# ============================================================
# 第1步：基因符号 → UniProt ID 映射
# ============================================================
print("\n第1步：映射到 UniProt ID...")

# 用 UniProt 的 ID Mapping API
# 提交任务
url = "https://rest.uniprot.org/idmapping/run"
params = {
    "from": "Gene_Name",
    "to": "UniProtKB",
    "ids": ",".join(symbols),
    "taxId": "9606",  # 人源
}
response = requests.post(url, data=params)
job_id = response.json()["jobId"]
print(f"  任务ID: {job_id}")

# 轮询等待任务完成
status_url = f"https://rest.uniprot.org/idmapping/status/{job_id}"
while True:
    status = requests.get(status_url).json()
    if "jobStatus" in status:
        print(f"  状态: {status['jobStatus']}")
        time.sleep(3)
    else:
        break

# 获取结果
result_url = f"https://rest.uniprot.org/idmapping/stream/{job_id}"
result = requests.get(result_url).json()
mapping = {}
for item in result.get("results", []):
    gene = item["from"]
    to_field = item["to"]
    if isinstance(to_field, dict):
        uniprot_id = to_field.get("primaryAccession")
    else:
        uniprot_id = to_field
    if gene not in mapping and uniprot_id:
        mapping[gene] = uniprot_id

print(f"  成功映射：{len(mapping)} 个")
print(f"  未映射：{len(set(symbols) - set(mapping.keys()))} 个")

# 保存映射表
map_df = pd.DataFrame([
    {"symbol": k, "uniprot_id": v} for k, v in mapping.items()
])
map_df.to_csv("data/gene_to_uniprot.csv", index=False)
print("  映射表已保存：data/gene_to_uniprot.csv")
print(map_df.head(10).to_string())

# ============================================================
# 第2步：下载蛋白质序列
# ============================================================
print("\n第2步：下载蛋白质序列...")

sequences = []
for i, (gene, uid) in enumerate(mapping.items()):
    try:
        url = f"https://rest.uniprot.org/uniprotkb/{uid}.fasta"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            lines = r.text.strip().split("\n")
            header = lines[0]
            seq = "".join(lines[1:])
            sequences.append({
                "symbol": gene,
                "uniprot_id": uid,
                "header": header,
                "sequence": seq,
                "length": len(seq),
            })
        else:
            print(f"  [{i+1}/{len(mapping)}] {gene} ({uid}) 失败: {r.status_code}")
    except Exception as e:
        print(f"  [{i+1}/{len(mapping)}] {gene} ({uid}) 异常: {e}")
    if (i + 1) % 10 == 0:
        print(f"  进度: {i+1}/{len(mapping)}")
    time.sleep(0.2)  # 避免请求过快

seq_df = pd.DataFrame(sequences)
seq_df.to_csv("data/ad_target_sequences.csv", index=False)

print(f"\n成功下载：{len(seq_df)} 条序列")
print(f"平均长度：{seq_df['length'].mean():.0f} 个氨基酸")
print()
print("前10条：")
print(seq_df[["symbol", "uniprot_id", "length"]].head(10).to_string())