# This is a fragment of a bash profile that I liked to use
# 
# Remember that bash looks for profile scripts in the following order:
#   $HOME/.bash_profile
#   $HOME/.bash_login
#   $HOME/.profile

export PAGER=less
export EDITOR=vi

# For shared systems, this is useful for automatically sourcing my personal setup script
#
# if [ "$($HOME/bruno/bin/incomingHost)" == "ibm750-r9rw756.raleigh.ibm.com" ]
# then
#   echo "$(hostname) welcomes Bruno"
#   source $HOME/bruno/setup
# fi

true

