## 1. create repo
	git clone git@github.west.isilon.com:$USER/onefs.git /path/folder
	git remote add isilon git@github.west.isilon.com:isilon/onefs.git
	git fetch --all --tags
	git fetch isilon
	git checkout -b BR_MAIN  isilon/BR_MAIN
	git checkout -b BR_PSCALE_115020
	branch

## 2. rename branch in local and remote
	git checkout <old_name>
	git branch -m <new_name>
	git push origin -u <new_name>
	git push origin BR_YAPPS2_112611
	git push origin --delete <old_name>

## 3. delete branch
	git branch -D BR_PSCALE_112611
	git push origin --delete BR_PSCALE_112611

## 4. upstream branch
	git branch --set-upstream-to=origin/BR_PSCALE_112611 BR_PSCALE_112611
	git checkout -b BR_PSCALE_115020 --track origin/BR_PSCALE_115020
	git branch -u origin/BR_PSCALE_115020 // already existed branch track remote branch
	

## 5. git config --global --edit
	% git config user.name
	Evers Chen
	% git config user.email
	evers_chen@163.com
	git config --global user.name "Evers Chen"
	git config --global user.email "evers_chen@163.com"


## 6. git Squash
	# List the shorthand version of the local tree. Change the "n" param to a number that will be at least as many commits as in the local change history +1
	git log --decorate=short -n 5 --single-worktree --oneline --graph
	# Pick one commit BEFORE the changes you want to make - the command is exclusive
	git rebase -i <commit ref>
	# change the "pick" to "squash" for any but the first line in the editor. This will squash all commits into the first one. Save & close.
	# When rebase runs, it will open an editor to ask for a new single message - choose only one and delete the rest of the non-commented lines
	git status # to show that only 1 outstanding commit remains with the desired message!

## 7. git rebase
	git fetch isilon
	git checkout BR_MAIN
	git pull
	git checkout BR_PSCALE_115025
	git rebase BR_MAIN
	git push
	git push -f

## 8. git diff 反向 apply
	git apply --reverse ~/update.diff

## 9. git worktree
	git branch -M BR_PSCALE_112611 BR_PSCALE_112611.original
	git worktree add BR_PSCALE_112611.original BR_PSCALE_112611.original
	git checkout -b BR_PSCALE_112611 isilon/BR_MAIN
	% git worktree list
		/ifs/home/echen1/git_test/main              e3dcdb8 [master]
		/ifs/home/echen1/git_test/dev               f86aec0 [dev]
		/ifs/home/echen1/git_test/new_folder        f86aec0 [my_test_branch]
		/ifs/home/echen1/git_test/new_folder/again  f86aec0 [again_branch]




