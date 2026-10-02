import pandas as pd
import requests
import time

mapping = pd.read_csv("data/gene_to_uniprot.csv")
print(f"待查询靶点：{len(mapping)} 个")

results = []
for i, row in mapping.iterrows():
    symbol = row["symbol"]
    uid = row["uniprot_id"]

    try:
        url = f"https://rest.uniprot.org/uniprotkb/{uid}.json"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            pdb_ids = []
            for xref in data.get("uniProtKBCrossReferences", []):
                if xref.get("database") == "PDB":
                    pdb_ids.append(xref["id"])
            results.append({
                "symbol": symbol,
                "uniprot_id": uid,
                "n_pdb": len(pdb_ids),
                "pdb_ids": ";".join(pdb_ids) if pdb_ids else "",
            })
        else:
            results.append({"symbol": symbol, "uniprot_id": uid, "n_pdb": -1, "pdb_ids": f"HTTP {r.status_code}"})
    except Exception as e:
        results.append({"symbol": symbol, "uniprot_id": uid, "n_pdb": -1, "pdb_ids": str(e)})

    if (i + 1) % 10 == 0:
        print(f"  进度: {i+1}/{len(mapping)}")
    time.sleep(0.3)

df = pd.DataFrame(results)
df.to_csv("data/ad_target_pdb_structures.csv", index=False)

print(f"\n查询完成")
print(f"有PDB结构的靶点：{len(df[df['n_pdb'] > 0])} 个")
print(f"无PDB结构的靶点：{len(df[df['n_pdb'] == 0])} 个")
print(f"查询失败的靶点：{len(df[df['n_pdb'] == -1])} 个")
print()
print("PDB结构最多的前15个靶点：")
print(df[df["n_pdb"] > 0].sort_values("n_pdb", ascending=False)[["symbol", "uniprot_id", "n_pdb"]].head(15).to_string())
print()
print("无PDB结构的靶点：")
print(df[df["n_pdb"] == 0][["symbol", "uniprot_id"]].to_string())