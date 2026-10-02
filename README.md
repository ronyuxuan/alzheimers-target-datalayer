# 阿尔茨海默病靶点数据层

从 Open Targets、UniProt、PDB 整合的阿尔茨海默病（AD）靶点数据集。

## 数据概览

- **靶点数量**: 93 个（globalScore ≥ 0.5）
- **数据来源**: Open Targets Platform, UniProt, RCSB PDB
- **数据快照**: 2026-10-02

## 数据字段

| 字段 | 说明 |
|---|---|
| symbol | 基因符号 |
| globalScore | AD 关联评分（0-1） |
| clinicalPrecedence | 临床先例评分 |
| uniprot_id | UniProt 蛋白质 ID |
| length | 蛋白质序列长度 |
| n_pdb | PDB 结构数量 |
| has_structure | 是否有 3D 结构 |

## 快速开始

```bash
pip install -r requirements.txt

python scripts/load_targets.py
python scripts/fetch_uniprot.py
python scripts/fetch_pdb.py
python scripts/merge_all.py
python scripts/generate_report.py

## 联系我

- GitHub: https://github.com/ronyuxuan
- 邮箱: ronyuxuan@126.com
- 有具体需求？欢迎在仓库提 Issue，或直接发邮件。
