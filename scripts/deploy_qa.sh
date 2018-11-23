#!/bin/sh
# Il parametro "resultTtlInSeconds" consente di configurare la durata della cache (in secondi)
# Impostandolo a 0 la cache viene disabilitata.
node_modules/serverless/bin/serverless deploy --stage qa --profile mygenerali-prod --resultTtlInSeconds 0 --playoff_hostname playoffgenerali.it