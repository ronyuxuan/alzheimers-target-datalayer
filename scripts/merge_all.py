import pandas as pd
import requests
import time

# ============================================================
# 第0步：补查失败的那1个靶点
# ============================================================
print("检查是否有查询失败的靶点...")
pdb_df = pd.read_csv("data/ad_target_pdb_structures.csv")
failed = pdb_df[pdb_df["n_pdb"] == -1]
if len(failed) > 0:
    print(f"  有 {len(failed)} 个失败，重试中...")
    for idx, row in failed.iterrows():
        uid = row["uniprot_id"]
        symbol = row["symbol"]
        for attempt in range(3):
            try:
                r = requests.get(f"https://rest.uniprot.org/uniprotkb/{uid}.json", timeout=60)
                if r.status_code == 200:
                    data = r.json()
                    pdb_ids = [x["id"] for x in data.get("uniProtKBCrossReferences", []) if x.get("database") == "PDB"]
                    pdb_df.loc[idx, "n_pdb"] = len(pdb_ids)
                    pdb_df.loc[idx, "pdb_ids"] = ";".join(pdb_ids)
                    print(f"  {symbol} 成功：{len(pdb_ids)} 个PDB")
                    break
            except Exception as e:
                time.sleep(3)
        time.sleep(0.5)
    pdb_df.to_csv("data/ad_target_pdb_structures.csv", index=False)
else:
    print("  无失败记录")

# ============================================================
# 第1步：读取所有数据源
# ============================================================
print("\n读取所有数据源...")
core = pd.read_csv("data/ad_core_targets.csv")           # symbol, globalScore, ...
seq = pd.read_csv("data/ad_target_sequences.csv")        # symbol, uniprot_id, sequence, length
pdb = pd.read_csv("data/ad_target_pdb_structures.csv")   # symbol, uniprot_id, n_pdb, pdb_ids

print(f"  核心靶点: {len(core)} 行")
print(f"  序列数据: {len(seq)} 行")
print(f"  PDB数据: {len(pdb)} 行")

# ============================================================
# 第2步：合并
# ============================================================
print("\n合并数据...")

# 只保留 core 里需要的列
core_subset = core[["symbol", "globalScore", "clinicalPrecedence"]].copy()

# 合并序列
df = core_subset.merge(
    seq[["symbol", "uniprot_id", "length"]],
    on="symbol",
    how="left"
)

# 合并 PDB
df = df.merge(
    pdb[["symbol", "n_pdb"]],
    on="symbol",
    how="left"
)

# 计算是否有结构
df["has_structure"] = df["n_pdb"] > 0

# 按 globalScore 降序
df = df.sort_values("globalScore", ascending=False).reset_index(drop=True)

# ============================================================
# 第3步：输出
# ============================================================
print(f"\n合并完成：{len(df)} 行 × {len(df.columns)} 列")
print()

print("=" * 60)
print("完整靶点数据表（前20）")
print("=" * 60)
print(df[["symbol", "globalScore", "uniprot_id", "length", "n_pdb", "has_structure"]].head(20).to_string())
print()

print("=" * 60)
print("统计摘要")
print("=" * 60)
print(f"  靶点总数: {len(df)}")
print(f"  有UniProt ID: {df['uniprot_id'].notna().sum()}")
print(f"  有序列: {df['length'].notna().sum()}")
print(f"  有PDB结构: {df['has_structure'].sum()}")
print(f"  无PDB结构: {(~df['has_structure']).sum()}")
print(f"  平均序列长度: {df['length'].mean():.0f} aa")
print(f"  globalScore 范围: {df['globalScore'].min():.4f} - {df['globalScore'].max():.4f}")

# 导出
df.to_csv("data/ad_target_master.csv", index=False)
print(f"\n主表已导出：data/ad_target_master.csv")