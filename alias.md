# my alias for easy use
	alias branch='git branch -vv'
	alias gitclean='git clean -f -x -d'
	alias submit='_submit(){ git add -u; if [[ "$1" != "" ]]; then git commit -m "$1"; else git commit; fi; git push --force; }; _submit'
	alias submitu='_submit(){ git add -u; git commit -m "update files";  git push --force; }; _submit'
	alias submita='_submit(){ git add -u; git commit --amend;  git push --force; }; _submit'
	alias rmfc='_rmfc(){ for i in "$1";do echo "rm $i\n"; yes | rm $i ;done ;}; _rmfc'
	alias uplift='_uplift(){ futurize --both-stages --write "$1"; black "$1";  reorder-python-imports "$1";  flake8 --config="ports/isilon/powerlint/files/config/flake8" "$1";}; _uplift'
	alias status="git status"