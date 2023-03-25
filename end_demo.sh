#!/bin/sh

docker compose down

rm ./realm/app_realm.json
rm ./realm/el_realm.json
rm ./realm/pcha_realm.json

rm ./docker-compose.yaml