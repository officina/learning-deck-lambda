#!/bin/sh
# Il parametro "resultTtlInSeconds" consente di configurare la durata della cache (in secondi)
# Impostandolo a 0 la cache viene disabilitata.
node_modules/serverless/bin/serverless deploy --profile mygenerali-dev --resultTtlInSeconds 0 -v