# wget https://ftp.ncbi.nlm.nih.gov/pub/lu/PubTator3/mutation2pubtator3.gz in December, 2024

cat mutation2pubtator3 | sort -nr | grep rs | head -31 | sed -E 's/rs0+/rs/' > pubtator_rs_latest_31.txt
cut -f 3 pubtator_rs_latest_31.txt | sort -u > rs_30.txt


# 後処理
# 1. dbSNPを検索してrs番号に対応するGene symbolを２列目に記載
# 2. rs1235072590は、rs80356821にmergeされたため、rs80356821に変更
#  https://www.ncbi.nlm.nih.gov/snp/rs1235072590
#  https://www.ncbi.nlm.nih.gov/snp/rs80356821 からGene symbolをHBBを取得