if [ ! -n "$1" ] ;then
        cur_branch="$1"
    echo "please input JIRA ID!"
        exit 1;
else
        expr $1 + 0 &>/dev/null
        tmp=`echo $1 |sed 's/[0-9]//g'`
        [ -n "${tmp}" ]&& { echo "please input integer for jira!";exit 1; }

        #echo ${tmp}

fi


jira=$1


git branch -vv

git checkout BR_MAIN
git pull

git checkout -b BR_PSCALE_$jira


CRTDIR=$(pwd)

workspace=$(basename $CRTDIR )

echo "set title to "$workspace-$jira
screen -X title $workspace-$jira

git push -u origin BR_PSCALE_$jira

git branch -vv

