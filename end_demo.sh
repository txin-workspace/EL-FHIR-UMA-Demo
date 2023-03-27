#!/bin/sh

echo "finish containers"
docker compose down

echo "delete realms jsons"
rm ./realm/app_realm.json
rm ./realm/el_realm.json
rm ./realm/pcha_realm.json

echo "delete compose yaml"
rm ./docker-compose.yaml

echo "delete postman jsons"
rm ./PostmanCollections/HAPI-FHIR.postman_collection.json
rm ./PostmanCollections/HAPI-RS.postman_collection.json
rm ./PostmanCollections/KeyCloak-API.postman_collection.json
rm ./PostmanCollections/ECHONETLite-RS.postman_collection.json

echo "finished"
