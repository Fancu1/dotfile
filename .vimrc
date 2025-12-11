" vim:

" ------------------------------------------------------------------------------
" general settings.
" ------------------------------------------------------------------------------
syntax on               " enable syntax highlighting

set nocompatible        " make Vim behave in a more useful way
set mouse=a             " enable mouse in all modes (normal, visual, etc)
set colorcolumn=80,100  " screen columns that are highlighted with ColorColumn
set backspace=2         " make backspace work like most other programs
set splitright          " if off, vsplit to left
set shiftwidth=2        " number of spaces to use for each step of (auto)indent
set tabstop=2           " number of spaces that a <tab> in the file counts for
set expandtab           " in insert mode: use spaces to insert a <tab>
set softtabstop=2       " number of spaces that a <tab> counts for while editing
set cindent             " indent for line according the C indenting rules
set noignorecase        " ignore case in a pattern
set noinfercase         " case sensitive for auto-complete
set showcmd             " show selecting area size in visual mode, cmd in normal
set nu                  " line number
set cursorline          " highlight the cursor line with CursorLine
set ruler               " show the line and column number of the cursor pos
set vb                  " use a visual bell instead of beeping
set modeline            " enable the 'modeline' option when editing a new file
set modelines=5         " must be set to enable modeline
set incsearch           " search pattern while typing in search.
set encoding=utf8       " character encoding
set nofoldenable        " disable fold in general.
set foldlevel=1         " folds with a higher level will be closed
set foldcolumn=0        " >0, show a col in the specified width indicating fold
set nospell             " disable spell. spelllang=en_us

set wildmenu            " possible matches are shown just above the command line
set wildmode=longest:full " emacs-style filename matching
set completeopt=longest,menuone " completion mode in insert mode

filetype plugin indent on
filetype plugin on

" disable netrw plugin which writes a .netrwhist file in ~/.vim when open dir
let g:loaded_netrw       = 1
let g:loaded_netrwPlugin = 1

" ------------------------------------------------------------------------------
" vim plugs
" ------------------------------------------------------------------------------
call plug#begin('~/.vim/plugged')

" --------
" tiled window management for Vim, like dwm
"
" <c-n> creates a new window and place it in the master pane [M] & stacks all
"       previous windows in the stacked pane [S]
" <c-c> close the current window if no unsaved changes
" <c-j> jumps to next window (clockwise)
" <c-k> jumps to previous window (anti-clockwise)
" <c-space>
"       focus the current window, that is, place it in the master pane [M] &
"       stacks all other windows in the stacked pane [S]
" --------
Plug 'xiejw/dwm.vim'

" --------
" airline.
" --------
Plug 'vim-airline/vim-airline', {'commit': 'f86f1e8' }  " 2017-06

" adjust: setup the fonts for ubuntu.
"
" follow https://github.com/powerline/fonts and select the font in termial
" profile (say xfce4-terminal with Droid Sans Mno Dotted for Powerline 9).
let g:airline#extensions#tabline#enabled = 1
let g:airline_section_b = '%{strftime("%c")}'
set laststatus=2

" ----
" fzf.
" ----
"
" search FZF_DEFAULT_COMMAND in bash_profile
Plug 'junegunn/fzf', { 'dir': '~/.fzf', 'do': './install --bin', 'commit': '9cb7a36'} " 2022-01
Plug 'junegunn/fzf.vim', {'commit': '70541d2'} " 2022-01

"---------
" dracula.
"---------
Plug 'dracula/vim', {'commit': 'b64b22a'} " 2020-08

" adjust: disable italic fonts to avoid the background highlight bugs.
"
" see https://github.com/dracula/vim/issues/81
let g:dracula_italic = 0

"------------
" indent line
"------------
Plug 'Yggdroot/indentLine', {'commit': '7753505'} " 2022-04
let g:indentLine_enabled = 0

call plug#end()

" ------------------------------------------------------------------------------
" colors configurations.
" ------------------------------------------------------------------------------

" --------
" dracula.
" --------
set background=dark " background must be set before colorscheme
colorscheme dracula

" ------------------
" color adjustments.
" ------------------
"
" define color for current line number. `set cursorline` must be set.
hi CursorLineNR ctermfg=Cyan
" define a special group for some languages, used in c, etc.
hi MyCKeyword ctermbg=DarkCyan ctermfg=Black
" change comment to darg green. makes it visible in terminal (usually is blue).
hi Comment ctermfg=DarkGreen
" make the visual selection more visible. 166 is orange.
hi visual ctermbg=166
" make the pop up menu more visible. 166 is orange.
hi PmenuSel ctermfg=White ctermbg=166

" ------------------------------------------------------------------------------
" leaders.
" ------------------------------------------------------------------------------
let mapleader = " "
set timeoutlen=500

" ---------------------------------
" refresh or save the file content.
" ---------------------------------
nmap <silent> <leader>r :e! <CR>
nmap <silent> <leader>s :update<CR>

" -----------------------
" navigation for buffers.
" -----------------------
nmap <silent> <leader>b :bn! <CR>
nmap <silent> <leader>B :bp! <CR>
nmap <silent> <leader>t :tabn <CR>
nmap <silent> <leader>T :tabp <CR>

" ------------------------------------
" some switches for spell, paste, etc.
" ------------------------------------
nmap <silent> <leader>p :set paste<CR>
nmap <silent> <leader>np :set nopaste<CR>
" nmap <silent> <leader>s :set spell<CR> " conflicted with save
" nmap <silent> <leader>ns :set nospell<CR>

" -------------------------------------------------------------------
" list the files to open, such as recent files, pending files in git.
" -------------------------------------------------------------------
nmap <silent> <leader>lb :call fns#LoadRecentFiles()<CR>
nmap <silent> <leader>ll :call fns#LoadPendingFiles()<CR>

" ----
" fzf.
" ----
nmap <silent> <leader>zz :FZF<cr>

" ----------
" indentLine
" ----------
nmap <silent> <leader>i :IndentLinesToggle<cr>

" -------------------
" open files related.
" -------------------
nmap <silent> <leader>ee :e %:p:h/
nmap <silent> <leader>et :tabnew %:p:h/

" ---------------------
" put `` and '' around a word.
" ---------------------
nmap <silent> <leader>` bi`<esc>wea`<esc>
nmap <silent> <leader>' bi'<esc>wea'<esc>

" ---------------------
" insert a 80-char line.
" ---------------------
nmap <silent> <leader>- i-<esc>79.
nmap <silent> <leader>= i=<esc>79.

" ---------------------
" insert a code block for help mode.
"
" ```
" >
"     <cursor>
" <
" ```
" ---------------------
nmap <silent> <leader>> i><esc>o<<esc>O<esc>i <esc>$<esc>4.a

" ------------------------------------------------------------------------------
" other Mappings.
" ------------------------------------------------------------------------------

" ---------------------------------------------
" kill the current buffer without losing split.
" ---------------------------------------------
nmap <silent> <leader>d :bp \| bd #<CR>
imap <tab> <c-x><c-p>

" ------------------------------------------------------------------------------
" filetype related.
" ------------------------------------------------------------------------------

" --- general
"
" delete tailing spaces for all lines (all files).
autocmd BufWritePre * :call fns#DelEmptyLinesEnd()

" --- general
"
" ask vim to check file timestamp (checktime). Once detected new change, due
" to `autoread`, the content will be loaded.
autocmd CursorHold * checktime
set autoread

" --- comments, formating, and pattern
"
" - comments is a comma separated list of string parts to start comments. A
"   part has format {flags}:{literal text}
"
" - formatoptions: a string that contains any letters below to control Vim fmt
"
"   t  Auto-wrap text using textwidth
"   c  Auto-wrap comments using textwidth, inserting the current comment
"      leader automatically.
"   r  Automatically insert the current comment leader after hitting
"      <enter> in Insert mode.
"   o  Automatically insert the current comment leader after hitting 'o' or
"      'O' in Normal mode.
"   q  Allow formatting of comments with "gq".
"      Note that formatting will not change blank lines or lines containing
"      only the comment leader.
"   n  When formatting text, recognize numbered lists.  This actually uses
"      the 'formatlistpat' option, thus any kind of list can be used. Note that
"      'autoindent' must be set too.  Doesn't work well together with "2".
"   2  When formatting text, use the indent of the second line of a paragraph
"      for the rest of the paragraph, instead of the indent of the first
"      line.  This supports paragraphs in which the first line has a
"      different indent than the rest.  Note that 'autoindent' must be set.
"
" - formatlistpat or flp:  A pattern that is used to recognize a list header.
"   This is used for the "n" flag in 'formatoptions'.
"
" - pattern
"
"     with `magic` on,
"
"         $      matches end-of-line
"         .      matches any character
"         *      any number of the previous atom
"         ~      latest substitute string
"         \(\)   grouping into an atom
"         \|     separating alternatives
"         \a     alphabetic character
"         \\     literal backslash
"         \.     literal dot
"         {      literal '{'
"         a      literal 'a'
"
"     see :h pattern.
"
"     for example, in search cmd, /a\(b\|c\) will search ab and ac.
"
"     for option value, the number of backslash is doubled. For example the
"     flp used in this vimrc. see :h option-backslash.
"

" --- vim
"
autocmd FileType vim :setlocal foldlevel=2 foldmethod=marker

" --- c
"
" - define some keywords with highlight color.
" - make header files as c not cpp.
" - set shift and tabstop per linux kernel style.
" - added more int types and error_t as cType
autocmd FileType c :match MyCKeyword /\<_mut_\|_out_\|_moved_in_\>/
autocmd BufRead,BufNewFile *.h setlocal filetype=c
autocmd FileType c :setlocal shiftwidth=8 tabstop=8 softtabstop=8
autocmd FileType c :syn keyword	cType	i64_t u64_t i32_t u32_t f32_t f64_t
autocmd FileType c :syn keyword	cType	vec_t error_t sds_t

" --- go
"
" - config flp: the list \s*-\s* in comments. The comment leader '//' is not
"   part of it
autocmd FileType go :setlocal tw=80
autocmd FileType go :setlocal comments=:// formatoptions=tcrqon
autocmd FileType go :setlocal flp=^\\s*-\\s*

" --- java
"
" - put record (since java 14) as similar syntax as `class`
"
autocmd FileType java :setlocal tw=80 shiftwidth=4
autocmd FileType java :syntax keyword javaClassDecl record

" --- scala
"
autocmd FileType scala :setlocal tw=80 shiftwidth=4

" --- text
"
autocmd FileType text :setlocal tw=80 nocindent smartindent

" --- markdown
"
" - config flp: for number list, the regexp is for number 1.\ and bullet -\
autocmd FileType markdown :setlocal tw=80 nocindent
autocmd FileType markdown :setlocal foldlevel=2
autocmd FileType markdown :setlocal foldmethod=expr foldexpr=fold#GetMarkdownFold(v:lnum)
autocmd FileType markdown :setlocal autoindent
autocmd FileType markdown :setlocal formatoptions+=n flp=^\\s*\\(\\d\\+\\.\\\|-\\)\\s

" --- makefile
"
autocmd FileType make :setlocal tw=80 nocindent
autocmd FileType make :setlocal shiftwidth=8 tabstop=8 softtabstop=8

" --- help
"
" - make Ignore highlight visible
" - disable hidding text with "conceal" syntax attr. For example, *tag* will
"   have the star showing instead of hiding.
" - make `pattern` and {pattern} more powerful than default configuration.
" - disable comments to avoid noise
" - set formatoptions as tcq2 to make the column format easier.
autocmd FileType help :hi Ignore ctermfg=DarkGreen
autocmd FileType help :setlocal conceallevel=0
autocmd FileType help :syn match helpOption  "'[-a-zA-Z0-9\_\."\(\) *+/:%#=[\]<.,]\+'"
autocmd FileType help :syn match helpSpecial "{[-a-zA-Z0-9\_\.'"\(\) *+/:%#=[\]<.,]\+}"
autocmd FileType help :setlocal comments=
autocmd FileType help :setlocal formatoptions=tcq
autocmd FileType help :setlocal autoindent nocindent
autocmd FileType help :setlocal formatoptions+=n flp=^\\s*\\(\\d\\+\\.\\\|-\\)\\s
autocmd FileType help :setlocal shiftwidth=4

" --- python
autocmd FileType python :setlocal tw=80
autocmd FileType python :setlocal shiftwidth=4
autocmd FileType python :setlocal foldlevel=1
autocmd FileType python :setlocal foldmethod=expr foldexpr=fold#GetPythonFold(v:lnum)

" --- plain tex
"
" customize the listing formatting ^\*\s according OPmac. So ::help fo-table
" autocmd FileType plaintex :setlocal formatoptions+=n flp=^\\*\\s
autocmd FileType plaintex :setlocal tw=80 nocindent
autocmd FileType plaintex :setlocal autoindent
autocmd FileType plaintex :setlocal formatoptions=tcq2

" --- bash
" customize the highlighting for function and its name. It was green, similar
" to the comment's color.
autocmd FileType bash :hi shFunctionKey ctermfg=Cyan
autocmd FileType bash :hi shFunction ctermfg=DarkBlue

" peixian --------------------------------------------------------------------------------
nnoremap J 4j
nnoremap K 4k

inoremap jj <Esc>
inoremap kk <Esc>
inoremap jk <Esc>
inoremap kj <Esc>
" 缩进之后, 不取消可视模式
xnoremap > >gv
xnoremap < <gv
vnoremap > >gv
vnoremap < <gv
" 移动到一个函数的开始
nnoremap <silent> <leader>u []
nnoremap <silent> <leader>d ][

" 移动到行首\行尾
nnoremap <silent> H ^
nnoremap <silent> L g_

" 删除一个单词
nnoremap <C-w> daw
