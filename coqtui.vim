" By Wang Nan @ 2017
try
    py import sys, vim
catch /E319:/
    if !exists('s:warned')
        echo "vim doesn't support python. Turn off coqtui"
        let s:warned = 1
    endif
    function! coqtui#Register()
    endfunction
    finish
endtry

let s:current_dir=expand("<sfile>:p:h") 
py if not vim.eval("s:current_dir") in sys.path:
\    sys.path.append(vim.eval("s:current_dir")) 
py import coqtui

function! coqtui#Launch(...)
    py coqtui.launch(*vim.eval("map(copy(a:000),'expand(v:val)')"))
endfunction

function! coqtui#Register()
    command! -bar -buffer -nargs=* -complete=file CoqLaunch call coqtui#Launch(<f-args>)
endfunction
