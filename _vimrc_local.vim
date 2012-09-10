"g* does a grep and puts results in the quickfix window
" The sequence of evil hackery:
" 1) Mark location globally with ("mZ")
" 2) Clear the quickfix list (":call setqflist([])<CR>")
" 3) Set hightlighting by making this local search too, but staying put ("*N")
" 4) Run :Ack command, searching in subdirectories, but not at the top level
"     (":Ack --literal --word-regexp <cword> **/*<CR>")
" 5) Hit the first result to reset focus to main window ("<CR>")
" 6) Go to wherever we were before this whole mess ('Z)
" 7) Reset focus to quickfix window
map <silent> g* mZ:call setqflist([])<CR>*N:Ack --ignore-dir=docs --literal --word-regexp <cword><CR><CR>'Z:copen<CR>
map <silent> gc* mZ:call setqflist([])<CR>*N:Ack --ignore-dir=docs --css --literal --word-regexp <cword><CR><CR>'Z:copen<CR>
map <silent> gl* mZ:call setqflist([])<CR>*N:Ack --ignore-dir=docs --less --literal --word-regexp <cword><CR><CR>'Z:copen<CR>

" Indentation prefs:
autocmd FileType javascript setlocal shiftwidth=2 tabstop=2
