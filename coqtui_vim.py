import vim

class CoqTUIView:
    main_buffer = None
    main_window = None
    goal_buffer = None
    goal_window = None
    info_buffer = None
    info_window = None
    def __init__(self):
        main_buffer = vim.current.buffer
        main_window = vim.current.window
        # create goals
        vim.command("rightbelow vnew Goals\n"\
                    "setlocal buftype=nofile\n"\
                    "setlocal filetype=coq-goals\n"\
                    "setlocal noswapfile\n"\
                    "setlocal nomodifiable\n"
        )
        goal_buffer = vim.current.buffer
        goal_window = vim.current.window
        vim.command("rightbelow new Infos\n"\
                    "setlocal buftype=nofile\n"\
                    "setlocal filetype=coq-goals\n"\
                    "setlocal noswapfile\n"\
                    "setlocal nomodifiable\n"
        )
        info_buffer = vim.current.buffer
        info_window = vim.current.window
        vim.command("%d.winc w" % main_window.number)

