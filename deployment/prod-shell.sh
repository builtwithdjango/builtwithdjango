ssh -t root@138.201.126.181 'docker exec -it $(docker ps --filter "name=srv-captain--bwd" | grep "^.*srv-captain--bwd\." | awk '\''{print $1}'\'') python manage.py shell_plus --ipython'
