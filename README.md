# mygenerali-lambda
## Setup di progetto
Il progetto si basa sull'utilizzo del framework *serverless*, tutto il necessario al setup del framework è descritto [qui](https://serverless.com/framework/docs/getting-started/).

Una volta completato il setup del framework, le principali operazioni potranno essere eseguite con i seguenti (tutti i comandi si intendono eseguiti all'interno della root del progetto):
+ **esecuzione locale della funzione play_action:** `sls invoke local -f play_action`
+ **esecuzione della funzione play_action effettivamente deployata:** `sls invoke -f play_action`
+ **deploy della lambda su remoto:** `sls deploy`
+ **visualizzazione dei logs di play_action:** `sls logs -f play_action -t`

## Tests



Per testare il mapping:

  python setup.py test

Per singoli test:

   python -m unittest tests.test_mapping.MappingTest.test_world_upgrade

##

Ho aggiunto la funzione che restituisce lo stato del giocatore che invoco come:

  serverless invoke local -f user_status -p tests/user.json

  serverless invoke local -f play_action_get -p play_input.json

Giocatori che non hanno giocato da una certa data:

serverless invoke local -f get_lazy_users -p tests/data/sls-get_lazy_users.json


## Scripts
All'interno della cartella scripts, oltre agli script per il deploy è presente lo script `clean_game_for_tests.py` che esegue la cancellazione 
di tutti i player di un gioco. E' necessario settare direttmaent e nello script il client che consente di accedere al gioco di interesse.