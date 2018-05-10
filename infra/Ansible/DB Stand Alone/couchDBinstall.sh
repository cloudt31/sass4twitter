echo "deb https://apache.bintray.com/couchdb-deb xenial main" | sudo tee -a /etc/apt/sources.list
curl -L https://couchdb.apache.org/repo/bintray-pubkey.asc | sudo apt-key add -
