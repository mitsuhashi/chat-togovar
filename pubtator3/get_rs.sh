# wget https://ftp.ncbi.nlm.nih.gov/pub/lu/PubTator3/mutation2pubtator3.gz
#cat mutation2pubtator3 | sort -nr | cut -f 3 | grep rs | sort -u | head -10 | sed -E 's/rs0+/rs/' > rs.txt

cat mutation2pubtator3 | sort -nr | grep rs | head -30 | sed -E 's/rs0+/rs/' > pubtator_latest_30.txt

cat mutation2pubtator3 | sort -nr | grep rs | cut -f 3 | head -30 | sed -E 's/rs0+/rs/' > rs.txt
