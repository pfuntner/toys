# This is a fragment of a bash profile that I liked to use
# 
# Remember that bash looks for profile scripts in the following order:
#   $HOME/.bash_profile
#   $HOME/.bash_login
#   $HOME/.profile

export PAGER=less
export EDITOR=vi
export PYTHONUNBUFFERED=true

# Windoze variables
if expr match "$(uname -s)" '.*[Ww][Ii][Nn]' >/dev/null 2>&1
then
  export ROOT=/cygdrive/c
  export GVIM=$ROOT/utils/gVimPortable/gVimPortable.exe
  export HOSTS=$ROOT/Windows/System32/drivers/etc/hosts
fi

# For shared systems, this is useful for automatically sourcing my personal setup script
#
# if [ "$($HOME/bruno/bin/incomingHost)" == "ibm750-r9rw756.raleigh.ibm.com" ]
# then
#   echo "$(hostname) welcomes Bruno"
#   source $HOME/bruno/setup
# fi

# For Windoze Cygwin only, set the mintty window title:
# echo -ne "\e]0;$(hostname)\a"

# This `true` statement must be last and will make sure that the this script returns with success regardless of what the previous command was.
true
