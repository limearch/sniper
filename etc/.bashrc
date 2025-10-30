# This file is running before loading the system shell.
# You can put anything here.

# The VIRTUAL_ENV variable give you the PSHMode path.
# You can use it to run files in etc folder.


function live_dir() {
	current_path=$(pwd)
	relative_path=$(realpath --relative-to="$HOME" "$current_path")
	formatted_path="~/$relative_path"

	if [[ "$current_path" == $HOME ]]; then
	    formatted_path="~${current_path#$HOME}"
	else
	    formatted_path="~/$relative_path"
	fi
	# printf("Done...!")
	echo "\u@\h:\w";
	# echo "$formatted_path";
}
echo $(live_dir)

# shortcuts
alias c="clear"
alias m="micro"
alias n="nano"
alias l="ls -CF"
alias la="ls -a"
alias gc="git clone"
alias p3i="pip3 install"
alias p2i="pip2 install"
alias pi="pip install"
alias cdSD="cd /sdcard"
alias cdDO="cd /sdcard/Download"

# colors
if [[ $BASH_VERSION != "" ]]; then
  LIGHT_RED="\[\033[1;40m\]"
  BLUE="\[\033[0;34m\]"
  LIGHT_BLUE="\[\033[1;34m\]"
  END_COLOR="\[\033[0m\]"
  END_BOLD=""
  LIVE_PATH="\W"
else
  LIGHT_RED="%B%{%F{blue}%}"
  BLUE="%B%{%F{cyan}%}"
  LIGHT_BLUE="%{%F{blue}%}"
  END_COLOR="%{%f%}"
  END_BOLD="%{%b%}"
  LIVE_PATH="~/$(realpath --relative-to="$HOME" $(pwd))"
fi


PROMPT_USERNAME="hack💀sniper"


# PSHMode prompt
PS1="${BLUE}┌──${BLUE}(${END_BOLD}${LIGHT_RED}$PROMPT_USERNAME${BLUE})${END_BOLD}${BLUE}-${BLUE}[${END_BOLD}${END_COLOR}$(live_dir)${BLUE}]${END_BOLD}"$'\n'"${BLUE}└─${LIGHT_RED}\$${END_BOLD}${END_COLOR} "

# ┌──(hack💀sniper)-[home]
# └─$
# PS1 = prompt()

unset LIGHT_RED BLUE LIGHT_BLUE END_COLOR END_BOLD LIVE_PATH
