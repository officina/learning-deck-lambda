#!/bin/sh
# Il parametro "resultTtlInSeconds" consente di configurare la durata della cache (in secondi)
# Impostandolo a 0 la cache viene disabilitata.
node_modules/serverless/bin/serverless deploy --profile default --region eu-west-1 --project_name lrm --stage prod --resultTtlInSeconds 0 --playoff_hostname playoffgamification.io
