# mygenerali-lambda
## Setup di progetto
Il progetto si basa sull'utilizzo del framework *serverless*, tutto il necessario al setup del framework è descritto [qui](https://serverless.com/framework/docs/getting-started/).

Una volta completato il setup del framework, le principali operazioni potranno essere eseguite con i seguenti (tutti i comandi si intendono eseguiti all'interno della root del progetto):
+ **esecuzione locale della funzione play_action:** `sls invoke local -f play_action` 
+ **esecuzione della funzione play_action effettivamente deployata:** `sls invoke -f play_action`
+ **deploy della lambda su remoto:** `sls deploy`
+ **visualizzazione dei logs di play_action:** `sls logs -f play_action -t`
