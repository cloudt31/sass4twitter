cd /opt/couchdb/etc/
#cp vm.args vm.args.old
IPA=$(hostname -I)
nIPA="$(echo -e "${IPA}" | sed -e 's/[[:space:]]*$//')"
curl -X PUT localhost:5984/_node/couchdb@"$nIPA"/_config/admins/admin -d '"cloudt3118"'
sleep 10
curl -X PUT http://admin:cloudt3118@localhost:5984/_node/couchdb@"$nIPA"/_config/chttpd/bind_address -d '"0.0.0.0"'
sleep 20
systemctl restart couchdb.service
