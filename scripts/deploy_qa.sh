#!/bin/sh
# Il parametro "resultTtlInSeconds" consente di configurare la durata della cache (in secondi)
# Impostandolo a 0 la cache viene disabilitata.
sls deploy --stage qa --profile mygenerali-prod --endpointType edge --resultTtlInSeconds 0