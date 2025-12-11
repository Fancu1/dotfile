# 防止cursor 卡住
if [[ "$TERM_PROGRAM" == "vscode" ]] || [[ -n "$CURSOR_TRACE_ID" ]]; then
  # 1. 关掉花里胡哨的东西
  unsetopt PROMPT_SUBST
  PROMPT='%n@%m:%~ %# '

  # 2. 若你有安装 shell integration，就手动 source 一下
  if command -v cursor >/dev/null 2>&1; then
    if [ -f "$(cursor --locate-shell-integration-path zsh 2>/dev/null)" ]; then
      source "$(cursor --locate-shell-integration-path zsh)"
    fi
  fi
fi

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

export ZSH="/Users/xsky/.oh-my-zsh"
export GOPATH=/Users/xsky/wpx/go
export GOROOT=/usr/local/go
export PATH=$GOPATH:$PATH:$GOROOT
export PATH=$HOME/.local/bin:$PATH
export PATH=/usr/local/opt/gnu-sed/libexec/gnubin:$PATH:$GOROOT/bin:$GOPATH/bin

# alias v="nvim"
alias wpx="cd /Users/xsky/wpx"
alias ggg="cd /Users/xsky/wpx/go/src"
alias xsky="cd /Users/xsky/wpx/xsky"
alias gs="git status"
alias ga="git add"
alias gcm="git commit -sm"
alias gca="git commit --amend -s"
alias gr="git rebase"
alias to="z"
alias ll="ls -lcht"
alias pssh="proxychains4 ssh"

# 镜像相关
alias di='docker image ls'
alias drm='docker image rm'

# 容器相关
alias dps='docker ps'
alias dpsa='docker ps -a'
alias dstop='docker stop'
alias drmcon='docker rm'

alias chrome="/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"

# my linux
alias tomylinux="multipass shell dev"
# alias enter_dev1="ssh -R 7890:127.0.0.1:7890 root@10.16.58.115"
alias enter_dev1="ssh root@10.16.58.115"
alias enter_myserver="proxychains4 ssh root@107.174.0.192 -p 9999"
alias enter_myserver2="proxychains4 ssh root@45.76.208.106 -p 9999"
alias enter_release="ssh root@release.xsky.com"
alias enter_gitbuilder='ssh -t gitbuilder@gitbuilder.xsky.com "cd gitbuilder.ceph.com && exec \$SHELL -l"'
export mylinux="192.168.64.2"

function proxy_on() {
    export https_proxy=http://127.0.0.1:7890
    export http_proxy=http://127.0.0.1:7890
    export all_proxy=socks5://127.0.0.1:7890
    echo "Proxy environment variable set."
}

function proxy_off() {
    unset http_proxy
    unset https_proxy
    unset all_proxy
    echo "Proxy environment variable unset."
}

#theme
ZSH_THEME="robbyrussell"

source $ZSH/oh-my-zsh.sh

source ~/.zplug/init.zsh

zplug "zsh-users/zsh-history-substring-search"
zplug "zdharma-continuum/fast-syntax-highlighting"
zplug "gustavohellwig/gh-zsh"
zplug "davidde/git"
zplug "zsh-users/zsh-autosuggestions"
zplug "skywind3000/z.lua"
zplug "jeffreytse/zsh-vi-mode"
zplug "MichaelAquilina/zsh-you-should-use"
zplug "ianthehenry/zsh-autoquoter"

if ! zplug check --verbose; then
    printf "Install? [y/N]: "
    if read -q; then
        echo; zplug install
    fi
fi

zplug load

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles
export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.aliyun.com/homebrew/homebrew-bottles
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

[[ -s "/Users/xsky/.gvm/scripts/gvm" ]] && source "/Users/xsky/.gvm/scripts/gvm"
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"
export HOMEBREW_NO_AUTO_UPDATE=true

. "$HOME/.atuin/bin/env"
export ATUIN_NOBIND="true"
eval "$(atuin init zsh)"
bindkey '^\\' atuin-search

# https://github.com/microsoft/inshellisense

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Added by Windsurf
export PATH="/Users/xsky/.codeium/windsurf/bin:$PATH"

