import csv, sys, json
P='/workspace/usethissi/metrics.csv'
vals=json.loads(sys.argv[1])
rows=list(csv.reader(open(P, newline='')))
hdr=rows[0]; assert len(hdr)==33
row=[str(vals.get(h,'')) for h in hdr]
rows=[hdr]+[r for r in rows[1:] if r and r[0]!=vals['date']]+[row]
rows[1:]=sorted(rows[1:], key=lambda r:r[0])
with open(P,'w',newline='') as f: csv.writer(f, lineterminator='\n').writerows(rows)
print(row)
