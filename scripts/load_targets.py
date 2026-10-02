import pandas as pd

# 读取 TSV 文件
df = pd.read_csv("data/alzheimers_targets.tsv", sep="\t")

print("=" * 60)
print("数据概览")
print("=" * 60)
print(f"行数：{len(df)}")
print(f"列数：{len(df.columns)}")
print()

print("前 10 个靶点（按 globalScore 排序）：")
print(df[["symbol", "globalScore", "clinicalPrecedence"]].head(10).to_string())
print()

# 把 "No data" 替换为 NaN
df_clean = df.replace("No data", pd.NA)

# 只对数值列做转换，跳过 symbol 列
for col in df_clean.columns:
    if col == "symbol":
        continue
    # 尝试转成数字，转不了的变成 NaN
    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

# 筛选：只保留有 globalScore 的靶点
df_clean = df_clean[df_clean["globalScore"].notna()].copy()

# 按 globalScore 降序排列
df_clean = df_clean.sort_values("globalScore", ascending=False)

print("=" * 60)
print("清洗后")
print("=" * 60)
print(f"有效靶点数：{len(df_clean)}")
print(f"globalScore 范围：{df_clean['globalScore'].min():.4f} - {df_clean['globalScore'].max():.4f}")
print()

print("前 20 个靶点：")
print(df_clean[["symbol", "globalScore", "clinicalPrecedence"]].head(20).to_string())
print()

# 看缺失情况
print("各列缺失率（前 10）：")
missing_rate = df_clean.isna().mean().sort_values(ascending=False)
print((missing_rate.head(10) * 100).round(1).to_string())
print()

# 导出
df_clean.to_csv("data/alzheimers_targets_clean.csv", index=False)
print(f"已导出：data/alzheimers_targets_clean.csv ({len(df_clean)} 行 × {len(df_clean.columns)} 列)")

# 筛选高置信度靶点
for threshold in [0.3, 0.5, 0.7]:
    n = len(df_clean[df_clean["globalScore"] >= threshold])
    print(f"globalScore >= {threshold}: {n} 个靶点")

# 取 globalScore >= 0.5 的靶点作为核心列表
core_targets = df_clean[df_clean["globalScore"] >= 0.5].copy()
core_targets.to_csv("data/ad_core_targets.csv", index=False)
print(f"\n核心靶点已导出：data/ad_core_targets.csv ({len(core_targets)} 个)")
print(core_targets[["symbol", "globalScore"]].head(30).to_string())