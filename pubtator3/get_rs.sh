# wget https://ftp.ncbi.nlm.nih.gov/pub/lu/PubTator3/mutation2pubtator3.gz in December, 2024

cat mutation2pubtator3 | sort -nr | grep rs | head -31 | sed -E 's/rs0+/rs/' > pubtator_rs_latest_31.txt
cut -f 3 pubtator_rs_latest_31.txt | sort -u > rs_30.txt
