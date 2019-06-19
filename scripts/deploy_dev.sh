#!/bin/sh
# Il parametro "resultTtlInSeconds" consente di configurare la durata della cache (in secondi)
# Impostandolo a 0 la cache viene disabilitata.
#export AWS_PROFILE=default
node_modules/serverless/bin/serverless deploy --profile learning-deck-dev --resultTtlInSeconds 0 -v
