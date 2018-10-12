import subprocess

bash_command = "sls invoke local -f get_user_status -p tests/data/data_get_user_status.json --region eu-central-1 --playoff_hostname playoffgenerali.it"
output,error = subprocess.Popen(['/bin/bash', '-c', bash_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
