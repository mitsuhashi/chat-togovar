# wget https://ftp.ncbi.nlm.nih.gov/pub/lu/PubTator3/mutation2pubtator3.gz
zgrep rs mutation2pubtator3.gz | cut -f 3 | sed -E 's/rs0+/rs/'  | uniq | head -10 > rs.txt
