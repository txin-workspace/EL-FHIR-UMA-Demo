#!/bin/sh

ADDR="$1"

if [ "$ADDR" = "" ]
then
    echo "need your ip v4 address"
    exit 9
fi

echo "Make AM server realm setting files"
sed "s/YOUR_ADDRESS/${ADDR}/g" ./realm/app_realm.template > ./realm/app_realm.json
sed "s/YOUR_ADDRESS/${ADDR}/g" ./realm/el_realm.template > ./realm/el_realm.json
sed "s/YOUR_ADDRESS/${ADDR}/g" ./realm/pcha_realm.template > ./realm/pcha_realm.json

echo "Make docker compose variable"
sed "s/YOUR_ADDRESS/${ADDR}/g" ./docker-compose.template > ./docker-compose.yaml

echo "Make postman collections variable"
sed "s/YOUR_ADDRESS/${ADDR}/g" ./PostmanCollections/HAPI-FHIR.postman_collection.temp > ./PostmanCollections/HAPI-FHIR.postman_collection.json
sed "s/YOUR_ADDRESS/${ADDR}/g" ./PostmanCollections/HAPI-RS.postman_collection.temp > ./PostmanCollections/HAPI-RS.postman_collection.json
sed "s/YOUR_ADDRESS/${ADDR}/g" ./PostmanCollections/KeyCloak-API.postman_collection.temp > ./PostmanCollections/KeyCloak-API.postman_collection.json
sed "s/YOUR_ADDRESS/${ADDR}/g" ./PostmanCollections/ECHONETLite-RS.postman_collection.temp > ./PostmanCollections/ECHONETLite-RS.postman_collection.json

echo "Start docker containers"
docker compose --verbose up -d --build

echo "Containers started , wait for all server ready"
docker container ls
