# my alias for easy use
	alias branch='git branch -vv'
	alias gitclean='git clean -fd'  //remove untracked files in git
	alias submit='_submit(){ git add -u; if [[ "$1" != "" ]]; then git commit -m "$1"; else git commit; fi; git push --force; }; _submit'
	alias submitu='_submit(){ update_files=`git status -s`; git add -u; git commit -m "update files: $update_files";  git push --force; }; _submit'
	alias submita='_submit(){ git add -u; git commit --amend;  git push --force; }; _submit'
	alias rmfc='_rmfc(){ for i in "$1";do echo "rm $i\n"; yes | rm $i ;done ;}; _rmfc'
	alias uplift='_uplift(){ futurize --both-stages --write "$1"; black "$1";  reorder-python-imports "$1";  flake8 --config="ports/isilon/powerlint/files/config/flake8" "$1";}; _uplift'
	alias status="git status"
	alias dt_create='_dt_create(){ if [[ "$2" != "" ]]; then dt vcluster create "$1" --location="$2" --num-nodes=3 --num-cpus=4 --password=a --qa --ignore-configure-errors; else dt vcluster create "$1" --location=sea1 --num-nodes=3 --num-cpus=4 --password=a --qa ; fi; }; _dt_create'
	alias fetch='git fetch --all --tags'
	clu='dt --owner echen1 vcluster list --pretty --pretty-columns name,id,build,expires,location,ips,state,provider_id,cost_per_hour --pretty-sort id'
	alias remove_ssh='_remove_ssh(){ ssh-keygen -f "/ifs/home/echen1/.ssh/known_hosts" -R "$1"; }; _remove_ssh'
	alias GDB='_GDB(){ pa=`which ${1%%.*}`;gdb $pa $1 ;}; _GDB'
	alias mykill='_mykill(){ pgrep -f "$1" | xargs kill ;}; _mykill'
	