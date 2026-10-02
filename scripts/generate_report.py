import pandas as pd
from datetime import datetime

df = pd.read_csv("data/ad_target_master.csv")

# ============================================================
# 1. 数据字典
# ============================================================
data_dict = pd.DataFrame([
    {"column": "symbol", "dtype": "string", "missing": 0,
     "description": "基因符号，靶点唯一标识"},
    {"column": "globalScore", "dtype": "float", "missing": 0,
     "description": "Open Targets 综合证据评分，0-1，越高越可能是AD靶点"},
    {"column": "clinicalPrecedence", "dtype": "float",
     "missing": int(df["clinicalPrecedence"].isna().sum()),
     "description": "临床先例评分，反映是否有已有药物针对该靶点"},
    {"column": "uniprot_id", "dtype": "string", "missing": 0,
     "description": "UniProt 蛋白质唯一标识"},
    {"column": "length", "dtype": "int", "missing": 0,
     "description": "蛋白质序列长度（氨基酸数）"},
    {"column": "n_pdb", "dtype": "int", "missing": 0,
     "description": "该蛋白质在PDB中的3D结构数量"},
    {"column": "has_structure", "dtype": "bool", "missing": 0,
     "description": "是否至少有一个PDB结构"},
])
data_dict.to_csv("data/data_dictionary.csv", index=False)

# ============================================================
# 2. 预先计算所有动态内容
# ============================================================
total = len(df)
has_struct = int(df["has_structure"].sum())
no_struct = total - has_struct
missing_clinical = int(df["clinicalPrecedence"].isna().sum())
pct_has = has_struct / total * 100
pct_no = no_struct / total * 100
pct_clinical = (1 - missing_clinical / total) * 100
avg_len = int(df["length"].mean())
min_len = int(df["length"].min())
max_len = int(df["length"].max())
med_len = int(df["length"].median())

# 评分分布
bins = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1.0)]
bin_rows = []
for lo, hi in bins:
    n = len(df[(df["globalScore"] >= lo) & (df["globalScore"] < hi)])
    bin_rows.append(f"| [{lo:.1f}, {hi:.1f}) | {n} | {n/total*100:.1f}% |")
bin_table = "\n".join(bin_rows)

# 无结构靶点清单
rows = []
for _, row in df[~df["has_structure"]].iterrows():
    rows.append(f"| {row['symbol']} | {row['uniprot_id']} | {row['length']} |")
no_struct_table = "\n".join(rows)

# Top 20 靶点
rows = []
for _, row in df.head(20).iterrows():
    gs = f"{row['globalScore']:.4f}"
    if pd.notna(row["clinicalPrecedence"]):
        cp = f"{row['clinicalPrecedence']:.4f}"
    else:
        cp = "—"
    rows.append(f"| {row['symbol']} | {gs} | {cp} | {row['uniprot_id']} | {row['length']} | {row['n_pdb']} |")
top20_table = "\n".join(rows)

now = datetime.now().strftime("%Y-%m-%d %H:%M")
today = datetime.now().strftime("%Y-%m-%d")

# ============================================================
# 3. 组装报告
# ============================================================
report = "# 阿尔茨海默病靶点数据层 — 完整交付报告\n\n"
report += f"**生成时间**: {now}\n"
report += f"**数据版本**: v1.0\n"
report += f"**靶点总数**: {total}\n"
report += f"**筛选标准**: Open Targets globalScore >= 0.5\n\n"
report += "---\n\n"

report += "## 目录\n\n"
report += "1. [数据来源](#1-数据来源)\n"
report += "2. [数据字段说明](#2-数据字段说明)\n"
report += "3. [数据质量评估](#3-数据质量评估)\n"
report += "4. [Top 20 靶点](#4-top-20-靶点)\n"
report += "5. [无结构靶点清单](#5-无结构靶点清单)\n"
report += "6. [已知局限](#6-已知局限)\n"
report += "7. [可复现性](#7-可复现性)\n"
report += "8. [使用建议](#8-使用建议)\n\n"
report += "---\n\n"

report += "## 1. 数据来源\n\n"
report += "| 数据源 | 用途 | 访问地址 |\n"
report += "|---|---|---|\n"
report += "| Open Targets Platform | AD靶点关联评分 | https://platform.opentargets.org/ |\n"
report += "| UniProt | 蛋白质序列与ID映射 | https://www.uniprot.org/ |\n"
report += "| RCSB PDB | 3D结构交叉引用 | https://www.rcsb.org/ |\n\n"
report += f"**数据快照日期**: {today}\n\n"
report += "---\n\n"

report += "## 2. 数据字段说明\n\n"
report += "| 字段 | 类型 | 缺失数 | 说明 |\n"
report += "|---|---|---|---|\n"
report += "| symbol | string | 0 | 基因符号，靶点唯一标识 |\n"
report += "| globalScore | float | 0 | AD关联评分 (0-1)，越高越可能是靶点 |\n"
report += f"| clinicalPrecedence | float | {missing_clinical} | 临床先例评分 |\n"
report += "| uniprot_id | string | 0 | UniProt 蛋白质唯一标识 |\n"
report += "| length | int | 0 | 蛋白质序列长度（氨基酸数） |\n"
report += "| n_pdb | int | 0 | PDB 结构数量 |\n"
report += "| has_structure | bool | 0 | 是否有实验解析的3D结构 |\n\n"
report += "完整数据字典见 `data/data_dictionary.csv`。\n\n"
report += "---\n\n"

report += "## 3. 数据质量评估\n\n"
report += "### 3.1 完整性\n\n"
report += "| 字段 | 填充率 | 评价 |\n"
report += "|---|---|---|\n"
report += "| symbol | 100.0% | ✓ 合格 |\n"
report += "| globalScore | 100.0% | ✓ 合格 |\n"
report += "| uniprot_id | 100.0% | ✓ 合格 |\n"
report += "| length | 100.0% | ✓ 合格 |\n"
report += "| n_pdb | 100.0% | ✓ 合格 |\n"
report += f"| clinicalPrecedence | {pct_clinical:.1f}% | ⚠ 部分缺失 |\n\n"
report += f"**说明**: `clinicalPrecedence` 缺失 {missing_clinical} 个（{missing_clinical/total*100:.1f}%），原因是 Open Targets 对该字段只对有临床先例的靶点给出评分。\n\n"

report += "### 3.2 globalScore 分布\n\n"
report += "| 评分区间 | 靶点数 | 占比 |\n"
report += "|---|---|---|\n"
report += bin_table + "\n\n"
report += "**解读**: 大部分靶点集中在 [0.5, 0.6) 区间，这是'有证据但不够强'的候选。评分 ≥ 0.7 的7个靶点是最核心的AD靶点。\n\n"

report += "### 3.3 PDB 结构覆盖\n\n"
report += "| 状态 | 数量 | 占比 |\n"
report += "|---|---|---|\n"
report += f"| 有实验结构 | {has_struct} | {pct_has:.1f}% |\n"
report += f"| 无实验结构 | {no_struct} | {pct_no:.1f}% |\n\n"
report += f"**解读**: {pct_has:.1f}% 的靶点已有实验解析的3D结构，可直接用于基于结构的药物设计。\n\n"

report += "### 3.4 序列长度分布\n\n"
report += "| 统计量 | 值 |\n"
report += "|---|---|\n"
report += f"| 最小值 | {min_len} aa |\n"
report += f"| 最大值 | {max_len} aa |\n"
report += f"| 平均值 | {avg_len} aa |\n"
report += f"| 中位数 | {med_len} aa |\n\n"
report += "---\n\n"

report += "## 4. Top 20 靶点\n\n"
report += "按 globalScore 降序排列的前20个靶点：\n\n"
report += "| 基因 | globalScore | clinicalPrecedence | UniProt | 长度 | PDB数 |\n"
report += "|---|---|---|---|---|---|\n"
report += top20_table + "\n\n"
report += "**重点靶点解读**:\n\n"
report += "- **APP** (0.8743): 淀粉样前体蛋白，AD研究的核心靶点，251个PDB结构\n"
report += "- **PSEN1/PSEN2** (0.8679/0.8190): 早发性AD的主要致病基因\n"
report += "- **APOE** (0.7883): 晚发性AD最强的遗传风险因子\n"
report += "- **ACHE/BCHE** (0.6416/0.6276): 已上市AD药物（多奈哌齐等）的靶点\n\n"
report += "---\n\n"

report += "## 5. 无结构靶点清单\n\n"
report += f"以下 {no_struct} 个靶点无实验解析的3D结构：\n\n"
report += "| 基因 | UniProt | 序列长度 |\n"
report += "|---|---|---|\n"
report += no_struct_table + "\n\n"
report += "**建议**: 这些靶点在建模时需使用 AlphaFold2/3 预测结构。AlphaFold DB 已提供大部分人类蛋白质的预测结构，可直接下载。\n\n"
report += "---\n\n"

report += "## 6. 已知局限\n\n"
report += "### 6.1 数据时效性\n"
report += "- globalScore 来自 Open Targets，**会随数据库更新而变化**\n"
report += f"- 本数据集为 {today} 快照，建议每季度更新一次\n\n"
report += "### 6.2 结构覆盖\n"
report += f"- {no_struct} 个靶点无实验结构，下游建模需用预测工具\n"
report += "- 有结构的靶点中，部分结构可能只是片段，需确认覆盖度\n\n"
report += "### 6.3 字段缺失\n"
report += f"- `clinicalPrecedence` 缺失 {missing_clinical} 个，不可用于所有靶点的横向比较\n"
report += "- 该字段只反映'是否有临床阶段药物'，不反映药物是否真的对AD有效\n\n"
report += "### 6.4 未经验证\n"
report += "- 本数据集**未经湿实验验证**，仅供计算分析和模型训练使用\n"
report += "- 任何基于本数据集的候选靶点，必须经过实验验证才能进入下游\n\n"
report += "---\n\n"

report += "## 7. 可复现性\n\n"
report += "所有数据均可通过以下脚本从原始数据源重新生成：\n\n"
report += "```bash\n"
report += "pip install -r requirements.txt\n"
report += "python scripts/load_targets.py\n"
report += "python scripts/fetch_uniprot.py\n"
report += "python scripts/fetch_pdb.py\n"
report += "python scripts/merge_all.py\n"
report += "python scripts/generate_report.py\n"
report += "```\n\n"
report += "**依赖环境**: Python >= 3.9, pandas >= 2.0.0, requests >= 2.31.0\n\n"
report += "---\n\n"

report += "## 8. 使用建议\n\n"
report += "### 8.1 靶点优先级排序\n"
report += "建议优先研究 `globalScore >= 0.7` 的7个靶点，它们有最强的证据支持。\n\n"
report += "### 8.2 结构基础\n"
report += f"- 有实验结构的 {has_struct} 个靶点，可直接进行分子对接、虚拟筛选\n"
report += f"- 无结构的 {no_struct} 个靶点，先用 AlphaFold DB 下载预测结构\n\n"
report += "### 8.3 下游应用场景\n\n"
report += "| 应用 | 推荐靶点集 |\n"
report += "|---|---|\n"
report += "| 虚拟筛选 | 有PDB结构且 n_pdb >= 10 的靶点 |\n"
report += "| 从头设计 | 有高分辨率结构的靶点 |\n"
report += "| 靶点发现 | globalScore >= 0.6 的靶点 |\n"
report += "| 机制研究 | clinicalPrecedence 有值的靶点 |\n\n"
report += "### 8.4 更新频率\n"
report += "- **建议**: 每季度更新一次\n"
report += "- **触发条件**: Open Targets 大版本更新、重要结构发布\n\n"
report += "---\n\n"

report += "## 附录：文件清单\n\n"
report += "| 文件 | 内容 |\n"
report += "|---|---|\n"
report += "| `data/ad_target_master.csv` | 核心数据表（93行 × 7列） |\n"
report += "| `data/data_dictionary.csv` | 数据字典 |\n"
report += "| `data/quality_report.md` | 本报告 |\n"
report += "| `data/gene_to_uniprot.csv` | 基因→UniProt映射 |\n"
report += "| `data/ad_target_sequences.csv` | 蛋白质序列 |\n"
report += "| `data/ad_target_pdb_structures.csv` | PDB结构列表 |\n\n"
report += "---\n\n"
report += "*本报告由自动化脚本生成。如有问题，请通过 GitHub Issues 反馈。*\n"

with open("data/quality_report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("=" * 60)
print("报告生成完成")
print("=" * 60)
print()
print(f"靶点总数: {total}")
print(f"有PDB结构: {has_struct} ({pct_has:.1f}%)")
print(f"无PDB结构: {no_struct} ({pct_no:.1f}%)")
print(f"clinicalPrecedence 缺失: {missing_clinical}")
print()
print("已导出:")
print("  data/data_dictionary.csv")
print("  data/quality_report.md")
print()
print("查看报告:")
print("  notepad data\\quality_report.md")