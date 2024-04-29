from tkinter.scrolledtext import ScrolledText
from tkinter import Tk


def SetWindowPos(
    window: Tk,
    relwidth: float = 0.5,
    relheight: float = 0.5,
    relx: float = 0.5,
    rely: float = 0.5,
) -> None:
    screen_width, screen_height = (
        window.winfo_screenwidth(),
        window.winfo_screenheight(),
    )

    width, height = int(screen_width * relwidth), int(screen_height * relheight)
    window_x, window_y = int((screen_width - width) * relx), int(
        (screen_height - height) * rely
    )

    window.geometry("%dx%d+%d+%d" % (width, height, window_x, window_y))
