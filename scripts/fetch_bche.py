import requests
import pandas as pd
import time

uid = "P06276"  # BCHE

for attempt in range(5):
    try:
        url = f"https://rest.uniprot.org/uniprotkb/{uid}.fasta"
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            lines = r.text.strip().split("\n")
            header = lines[0]
            seq = "".join(lines[1:])
            print(f"成功：BCHE ({uid})")
            print(f"长度：{len(seq)} 个氨基酸")
            print(f"序列前50字符：{seq[:50]}...")

            # 追加到已有文件
            df = pd.read_csv("data/ad_target_sequences.csv")
            new_row = pd.DataFrame([{
                "symbol": "BCHE",
                "uniprot_id": uid,
                "header": header,
                "sequence": seq,
                "length": len(seq),
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv("data/ad_target_sequences.csv", index=False)
            print(f"\n已追加。现在共 {len(df)} 条序列")
            break
        else:
            print(f"第{attempt+1}次失败：{r.status_code}")
            time.sleep(5)
    except Exception as e:
        print(f"第{attempt+1}次异常：{e}")
        time.sleep(5)