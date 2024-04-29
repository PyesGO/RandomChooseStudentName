import os as _os
import random as _random
import sys as _sys
import tkinter as _tk
import typing as _tp
from collections import deque as _deque
from functools import partial as _partial
from functools import wraps as _wraps
from tkinter import filedialog as _filedialog
from tkinter import messagebox as _messagebox
from tkinter import ttk as _ttk

import config as _config
import ExMethods as _TkExMethods


GLOBAL_FONT = "Microsoft YaHei" if _sys.platform == "win32" else ""


class CustomWidget(object):
    def __init__(self, master: _tk.Misc) -> None:
        self._w: _tp.Union[_ttk.Frame, _ttk.Labelframe]

    @property
    def root(self) -> _tp.Union[_ttk.Frame, _ttk.Labelframe]:
        return self._w

    frame = root


class FontInfo(_tp.NamedTuple):
    font: str
    font_size: int
    row_height: _tp.Optional[int]


class NameInfo(_tp.NamedTuple):
    name: str
    sex: str
    state: str
    remakes: str


class DrawItem(_tp.NamedTuple):
    item_id: int
    name_info: NameInfo


class DrawNameListEvent(_tp.NamedTuple):
    event_type: str
    callback: _tp.Callable
    args: _tp.ParamSpecArgs


class NameList(CustomWidget):
    def __init__(
        self,
        master: _tk.Misc,
        headings: dict[str, str],
        anchor: str = _tk.CENTER,
        font: str = GLOBAL_FONT,
        font_size: int = 11,
        rowheight: _tp.Optional[int] = None,
    ) -> None:
        """Provides a basic encapsulation for NameList."""

        self._font_info = FontInfo(font=font, font_size=font_size, row_height=rowheight)

        self._treeview_style: _ttk.Style = _ttk.Style()

        self.font_configure(self._font_info)

        self._frame_root = self._w = _ttk.Frame(master)
        self._treeview = _ttk.Treeview(
            self._frame_root,
            show="headings",
            columns=tuple(headings.keys()),
            style="Namelist.Treeview",
            height=0,
            selectmode=_tk.BROWSE,
        )
        self._treeview_scrollbar = _ttk.Scrollbar(self._frame_root, orient=_tk.VERTICAL)

        self._treeview.configure(yscrollcommand=self._treeview_scrollbar.set)
        self._treeview_scrollbar.configure(command=self._treeview.yview)

        self._treeview.pack_configure(fill=_tk.BOTH, side=_tk.LEFT, expand=_tk.YES)
        self._treeview_scrollbar.pack_configure(fill=_tk.Y, side=_tk.RIGHT)

        for column_id, column_name in headings.items():
            self._treeview.heading(column=column_id, anchor=anchor, text=column_name)
            self._treeview.column(
                column=column_id, anchor=anchor, stretch=_tk.YES, width=0
            )

    @property
    def treeview_children(self) -> tuple[str, ...]:
        return self._treeview.get_children()

    @property
    def selected_items(self) -> tuple[str, ...]:
        return self._treeview.selection()

    @property
    def font_info(self) -> FontInfo:
        return self._font_info

    def clear_info(self) -> None:
        self._treeview.delete(*self.treeview_children)

    @_tp.overload
    def font_configure(self, font_info: FontInfo) -> None:
        ...

    @_tp.overload
    def font_configure(self, *, font: str, font_size: int) -> None:
        ...

    @_tp.overload
    def font_configure(self, *, font: str, font_size: int, row_height: int) -> None:
        ...

    def font_configure(
        self,
        font_info: _tp.Optional[FontInfo] = None,
        **kwds: _tp.Union[str, int],
    ) -> None:
        if kwds:
            font_info = FontInfo(
                font=kwds.pop("font"),
                font_size=kwds.pop("font_size"),
                row_height=kwds.pop("row_height", None),
            )
        elif not font_info:
            raise TypeError("font_info or font parameters must be selected to pass in.")

        self._treeview_style.configure(
            style="Namelist.Treeview",
            rowheight=(font_info.row_height)
            or int(
                font_info.font_size
                * 1.4
                * self._treeview_style.tk.call("tk", "scaling")
            ),
            font=(font_info.font, font_info.font_size),
        )

        self._font_info = font_info

    def adapt_touch_screen(self) -> None:
        self._touch_pointer_y = self._touch_treeview_height = 0
        self._touch_original_fraction = 0.0

        def _mouse_release(event: _tk.Event) -> None:
            self._treeview.unbind("<Motion>")

        def _mouse_move(event: _tk.Event) -> None:
            pointer_fraction = (
                self._touch_pointer_y - event.y
            ) / self._touch_treeview_height
            fraction = self._touch_original_fraction + pointer_fraction
            self._treeview.yview_moveto(fraction)

        def _mouse_press(event: _tk.Event) -> None:
            self._touch_pointer_y = event.y
            self._touch_original_fraction = self._treeview.yview()[0]
            self._touch_treeview_height = self._treeview.winfo_height()
            self._treeview.bind("<Motion>", _mouse_move)

        self._treeview.bind("<ButtonPress-1>", _mouse_press)
        self._treeview.bind("<ButtonRelease-1>", _mouse_release)

    def unadapt_touch_screen(self) -> None:
        if "_touch_pointer_y" in self.__dict__:
            self._treeview.unbind("<ButtonPress-1>")
            self._treeview.unbind("<ButtonRelease-1>")
            for n in tuple(self.__dict__.keys()):
                if n.startswith("_touch"):
                    delattr(self, n)


class DrawNameList(NameList):
    MALE = "男"
    FEMALE = "女"
    EN = "英语"
    JP = "日语"
    NONE = "无备注"
    NOT_DRAWN = "未抽过"
    DRAWN = "已抽过"
    DELETED = "已删除"

    FLAGS_MALE = MALE
    FLAGS_FEMALE = FEMALE
    FLAGS_EN = EN
    FLAGS_JP = JP
    FLAGS_NONE = NONE
    FLAGS_NOT_DRAWN = NOT_DRAWN
    FLAGS_DRAWN = DRAWN
    FLAGS_DELETED = DELETED

    ITEM_NAME = "name"
    ITEM_SEX = "sex"
    ITEM_STATE = "state"
    ITEM_REMAKES = "remakes"

    EVENT_LOAD = "load"
    EVENT_CLEAR = "clear"
    EVENT_RESET = "reset"

    OPTIONS_STATE = _tp.Literal["未抽过", "已抽过", "已删除"]
    OPTIONS_SEX = _tp.Literal["男", "女"]
    OPTIONS_REMAKES = _tp.Literal["英语", "日语", "无备注"]
    OPTIONS_EVENT = _tp.Literal["load", "clear", "reset"]

    def __init__(self, master: _tk.Misc) -> None:
        """Namelist."""
        super().__init__(
            master=master, headings=dict(name="名字", sex="性别", state="状态", remakes="备注")
        )
        self._callbacks: list[DrawNameListEvent] = []

    @staticmethod
    def join(__info: NameInfo, /) -> str:
        return "-".join(__info)

    @staticmethod
    def split(__iteminfo: str, /) -> NameInfo:
        return NameInfo(*__iteminfo.split("-"))

    @property
    def treeview_items(self) -> list[NameInfo]:
        return [self.get_info(i) for i in self.treeview_children]

    @property
    def selected_item(self) -> _tp.Optional[str]:
        if items := self.selected_items:
            return items[0]

    @_tp.overload
    def insert_info(self, name_info: NameInfo) -> str:
        ...

    @_tp.overload
    def insert_info(
        self,
        *,
        name: str,
        sex: OPTIONS_SEX,
        state: OPTIONS_STATE,
        language: OPTIONS_REMAKES,
    ) -> str:
        ...

    def insert_info(self, name_info: _tp.Optional[NameInfo] = None, **kwds: str) -> str:
        if (not name_info) and kwds:
            name_info = NameInfo(
                name=kwds["name"],
                sex=kwds["sex"],
                state=kwds["state"],
                remakes=kwds["language"],
            )
        elif not kwds:
            raise TypeError("name_info or name parameters must be selected to pass in.")

        return self._treeview.insert(
            "", _tk.END, self.join(name_info), values=name_info
        )

    def execute_callback(self, event_type: OPTIONS_EVENT) -> None:
        for cb in self._callbacks:
            if event_type == cb.event_type:
                cb.callback(*cb.args)

    def register_event_callback(
        self, event_type: OPTIONS_EVENT, callback: _tp.Callable, *args
    ) -> None:
        self._callbacks.append(DrawNameListEvent(event_type, callback, args))

    def get_specific_info(
        self,
        spec_item: str,
        spec_flags: str,
        info_list: _tp.Optional[list[NameInfo]] = None,
    ) -> list[NameInfo]:
        if not info_list:
            info_list = self.treeview_items
        return [i for i in info_list if getattr(i, spec_item) == spec_flags]

    def get_info(self, item: str) -> NameInfo:
        return NameInfo._make(self._treeview.item(item)["values"])

    def get_selected_info(self) -> _tp.Optional[NameInfo]:
        if item := self.selected_item:
            return self.get_info(item)

    def modify_selected_info(self, __info: NameInfo, /) -> None:
        if item := self.selected_item:
            self.modify_specific_item(self.split(item), __info)

    @_tp.overload
    def modify_specific_item(
        self,
        source_info: NameInfo,
        dest_info: NameInfo,
    ) -> None:
        ...

    @_tp.overload
    def modify_specific_item(
        self,
        source_info: NameInfo,
        *,
        name: str = ...,
        sex: OPTIONS_SEX = ...,
        state: OPTIONS_STATE = ...,
        language: OPTIONS_REMAKES = ...,
    ) -> None:
        ...

    def modify_specific_item(
        self,
        source_info: NameInfo,
        dest_info: _tp.Optional[NameInfo] = None,
        **kwds,
    ) -> None:
        if dest_info:
            replaced_info = dest_info
        else:
            replaced_info = source_info._replace(**kwds)

        source_item_id = self.join(source_info)
        source_item_index = self._treeview.index(source_item_id)

        self._treeview.delete(source_item_id)

        dest_item_id = self.insert_info(replaced_info)
        self._treeview.move(dest_item_id, "", source_item_index)

    def delete_selected_item(self) -> _tp.Optional[NameInfo]:
        if item := self.selected_item:
            info = self.get_info(item)
            self._treeview.delete(item)
            return info

    def clear_all_item(self) -> None:
        if items := self.treeview_children:
            self._treeview.delete(*items)
            self.execute_callback(self.EVENT_CLEAR)

    def load(self, filepath: _tp.Optional[str] = None, dialog: bool = True) -> None:
        if (not filepath) and (dialog):
            filepath = _filedialog.askopenfilename(
                filetypes=[("TXT文本文档", "*.txt")], title="选择一个文件"
            )

        if (filepath) and (_os.path.exists(filepath)):
            _rp = {
                "f": DrawNameList.FEMALE,
                "m": DrawNameList.MALE,
                "e": DrawNameList.EN,
                "j": DrawNameList.JP,
            }
            with open(filepath, "rt", encoding="UTF-8") as fp:
                while (_line := fp.readline().strip()) != "":
                    _name, _sex, _remakes = _line[:-2], _line[-2], _line[-1]
                    _sex, _remakes = _rp[_sex], _rp[_remakes]
                    self.insert_info(
                        name=_name,
                        state=DrawNameList.NOT_DRAWN,
                        sex=_sex,
                        language=_remakes,
                    )
            self.execute_callback(self.EVENT_LOAD)
        else:
            print("The specified file path does not exist.")

    def reset(self) -> None:
        for i in self.treeview_items:
            self.modify_specific_item(i, state=self.NOT_DRAWN)
        else:
            self.execute_callback(self.EVENT_RESET)


def NameInfoChanger(
    master: _tk.Tk,
    title: str = "名字信息",
    relwidth: float = 0.2,
    relheight: float = 0.15,
    default_info: _tp.Optional[_tp.Union[NameInfo, tuple[str, str, str]]] = None,
) -> _tp.Optional[NameInfo]:
    """View or modify information."""
    result = ("", "", "")

    top = _tk.Toplevel()
    top.wm_withdraw()
    _TkExMethods.SetWindowPos(window=top, relwidth=relwidth, relheight=relheight)
    top.wm_transient(master)
    top.wm_title(title)
    top.configure(borderwidth=5)

    literals = ("名字:", "性别:", "备注:")
    literals_widgets = (
        _ttk.Entry(top),
        _ttk.Combobox(top, values=(DrawNameList.MALE, DrawNameList.FEMALE)),
        _ttk.Combobox(top, values=(DrawNameList.EN, DrawNameList.JP)),
    )

    if isinstance(default_info, NameInfo):
        default_info = (default_info.name, default_info.sex, default_info.remakes)
    else:
        default_info = result

    row = column = 0
    for txt, widget, info in zip(literals, literals_widgets, default_info):
        kwds = {}
        if row == 1:
            kwds["pady"] = 5
        label = _ttk.Label(top, text=txt)
        label.grid_configure(cnf=kwds, row=row, column=column, sticky=_tk.E)
        column += 1
        widget.grid_configure(cnf=kwds, row=row, column=column, sticky=_tk.EW)
        widget.insert(_tk.END, info)
        top.grid_columnconfigure(column, weight=1)
        row += 1
        column = 0
        if row == 2:
            widget.configure(state="readonly")

    def _release(confirm: bool) -> None:
        nonlocal result
        if confirm:
            result = [w.get() for w in literals_widgets]
        top.grab_release()
        top.destroy()

    button_confirm = _ttk.Button(
        top, text="确认", command=_partial(_release, True), default=_tk.ACTIVE
    )
    button_cancel = _ttk.Button(top, text="取消", command=_partial(_release, False))
    button_confirm.place_configure(anchor=_tk.SW, relx=0.0, rely=1.0, relwidth=0.49)
    button_cancel.place_configure(anchor=_tk.SE, relx=1.0, rely=1.0, relwidth=0.49)

    literals_widgets[0].focus_set()
    top.grab_set()
    top.wm_deiconify()
    top.wm_protocol("WM_DELETE_WINDOW", _partial(_release, False))
    top.wait_window()

    if all(result):
        name, sex, remakes = result
        return NameInfo(
            name=name, sex=sex, state=DrawNameList.NOT_DRAWN, remakes=remakes
        )


class NameListControl(CustomWidget):
    def __init__(
        self, master: _tk.Misc, namelist: DrawNameList, recyle_namelist: DrawNameList
    ) -> None:
        """Control namelist widget."""
        self._namelist = namelist
        self._recyle_namelist = recyle_namelist

        self._frame_root = self._w = _ttk.Frame(master)
        self._button_add = _ttk.Button(
            self._frame_root, text="添加", command=self._add, default=_tk.ACTIVE
        )
        self._button_change = _ttk.Button(
            self._frame_root, text="修改", command=self._change
        )
        self._button_delete = _ttk.Button(
            self._frame_root, text="删除", command=self._delete
        )
        self._button_restore = _ttk.Button(
            self._frame_root, text="还原", command=self._restore
        )
        self._button_clear_all = _ttk.Button(
            self._frame_root, text="清空", command=self._namelist.clear_all_item
        )
        self._button_load = _ttk.Button(
            self._frame_root, text="导入", command=self._namelist.load
        )

        self._button_add.pack_configure(expand=_tk.YES, fill=_tk.BOTH, side=_tk.LEFT)
        self._button_change.pack_configure(
            expand=_tk.YES, fill=_tk.BOTH, side=_tk.LEFT, padx=2
        )
        self._button_delete.pack_configure(expand=_tk.YES, fill=_tk.BOTH, side=_tk.LEFT)
        self._button_restore.pack_configure(
            expand=_tk.YES, fill=_tk.BOTH, side=_tk.LEFT, padx=2
        )
        self._button_clear_all.pack_configure(
            expand=_tk.YES, fill=_tk.BOTH, side=_tk.LEFT
        )
        self._button_load.pack_configure(
            expand=_tk.YES, fill=_tk.BOTH, side=_tk.LEFT, padx=(2, 0)
        )

    def _set_btns_state(self, __ns_btns: tuple[_ttk.Button], __state: str, /) -> None:
        for btn in __ns_btns:
            btn.configure(state=__state)

    def _add(self) -> None:
        if info := NameInfoChanger(self._frame_root):
            self._namelist.insert_info(info)

    def _change(self) -> None:
        if (original_info := self._namelist.get_selected_info()) is not None:
            if original_info != (
                info := NameInfoChanger(self._frame_root, default_info=original_info)
            ):
                self._namelist.modify_selected_info(info)

    def _delete(self) -> None:
        if info := self._namelist.delete_selected_item():
            self._recyle_namelist.insert_info(info)

    def _restore(self) -> None:
        if info := self._recyle_namelist.delete_selected_item():
            self._namelist.insert_info(info)


class InfoShower(CustomWidget):
    COLOR_DRAWN = "red"
    COLOR_NOT_DRAWN = "skyblue"

    STATE_COLOR = _tp.Literal["red", "skyblue"]

    def __init__(self, master: _tk.Misc) -> None:
        """Information shower."""
        self._frame_root = self._w = _ttk.Frame(master)
        self._frame_text = _ttk.Labelframe(
            self._frame_root, text="蓝色未抽|红色已抽", borderwidth=2
        )
        self._frame_namelist = _ttk.Labelframe(
            self._frame_root,
            text="名字列表",
            borderwidth=2,
        )
        self._frame_recyle_nl = _ttk.Labelframe(
            self._frame_root,
            text="删除历史",
            borderwidth=2,
        )

        self._text_draw_state = _TkExMethods.ScrolledText(
            self._frame_text,
            relief=_tk.FLAT,
            state=_tk.DISABLED,
            font=(GLOBAL_FONT, 11),
        )
        self._namelist = DrawNameList(self._frame_namelist)
        self._recyle_nl = DrawNameList(self._frame_recyle_nl)
        self._nl_control = NameListControl(
            self._frame_root, self._namelist, self._recyle_nl
        )
        pack_cnf = dict(expand=_tk.YES, fill=_tk.BOTH)
        self._text_draw_state.pack_configure(cnf=pack_cnf)
        self._namelist.frame.pack_configure(cnf=pack_cnf)
        self._recyle_nl.frame.pack_configure(cnf=pack_cnf)

        self._frame_text.place_configure(relwidth=1.0, relheight=0.45)
        self._frame_namelist.place_configure(
            relx=0.0, rely=0.45, relwidth=0.5, relheight=0.45
        )
        self._frame_recyle_nl.place_configure(
            relx=0.5, rely=0.45, relwidth=0.5, relheight=0.45
        )
        self._nl_control.frame.place_configure(
            relx=0.0, rely=0.9, relwidth=1.0, relheight=0.1
        )

        self._namelist.register_event_callback(
            DrawNameList.EVENT_LOAD, self.init_state_info
        )

        # Some interal function.
        self.get_infolist = _partial(
            self._namelist.get_specific_info, DrawNameList.ITEM_STATE
        )
        self.get_drawn_infolist = _partial(self.get_infolist, DrawNameList.FLAGS_DRAWN)
        self.get_not_drawn_infolist = _partial(
            self.get_infolist, DrawNameList.FLAGS_NOT_DRAWN
        )
        self.get_drawn_names = lambda: [n.name for n in self.get_drawn_infolist()]
        self.get_not_drawn_names = lambda: [
            n.name for n in self.get_not_drawn_infolist()
        ]

    @staticmethod
    def _modify_text(func: _tp.Callable):
        def _inner(self, *args, **kwargs):
            self._text_draw_state.configure(state=_tk.NORMAL)
            func(self, *args, **kwargs)
            self._text_draw_state.configure(state=_tk.DISABLED)

        return _inner

    def _update_names_text_bgcolor(self, *names: str, color: STATE_COLOR) -> None:
        for n in names:
            self._text_draw_state.tag_configure(n, background=color)

    def _update_text(self) -> None:
        self._update_names_text_bgcolor(*self.get_drawn_names(), color=self.COLOR_DRAWN)
        self._update_names_text_bgcolor(
            *self.get_not_drawn_names(), color=self.COLOR_NOT_DRAWN
        )

    def _prep_name_text_tags(self, names: _tp.Iterable[str]) -> None:
        row_index = 1
        start_column_index = 0
        for n in names:
            end_column_index = start_column_index + len(n)
            self._text_draw_state.tag_add(
                n,
                "%d.%d" % (row_index, start_column_index),
                "%d.%d" % (row_index, end_column_index),
            )
            start_column_index = end_column_index + 1

    @_modify_text
    def _init_state_info(self) -> None:
        if self._text_draw_state.get(0.0, _tk.END):
            self._text_draw_state.delete(0.0, _tk.END)
        if self._text_draw_state.tag_names():
            self._text_draw_state.tag_delete(_tk.ALL)

        names = [info.name for info in self._namelist.treeview_items]
        self._text_draw_state.insert(_tk.END, " ".join(names))

        self._prep_name_text_tags(names)
        self._update_names_text_bgcolor(*names, color=self.COLOR_NOT_DRAWN)

    @_modify_text
    def _update_state(
        self,
        *info: NameInfo,
        state: DrawNameList.OPTIONS_STATE = DrawNameList.FLAGS_DRAWN,
    ) -> None:
        for i in info:
            self._namelist.modify_specific_item(i, state=state)
        self._update_text()

    @_tp.overload
    def update_state(
        self,
        *info: NameInfo,
        state: DrawNameList.OPTIONS_STATE = DrawNameList.FLAGS_DRAWN,
    ) -> None:
        ...

    def update_state(self, *args, **kwargs) -> None:
        return self._update_state(*args, **kwargs)

    def init_state_info(self) -> None:
        return self._init_state_info()

    @property
    def namelist(self) -> DrawNameList:
        return self._namelist

    @property
    def recyle_namelist(self) -> DrawNameList:
        return self._recyle_nl


class DrawOptions(CustomWidget):
    def __init__(self, master: _tk.Misc) -> None:
        self._frame_root = self._w = _ttk.Labelframe(master, text="筛选")

        literals = ("按性别:", "按类型:")
        rad_btn_liters = ("只抽男生", "只抽女生", "无限制", "只抽英语", "只抽日语", "只抽无备注", "无限制")
        rad_btn_values = (
            _config.CS_SPEC_SEX_MALE,
            _config.CS_SPEC_SEX_FEMALE,
            _config.CS_NONE,
            _config.CS_SPEC_TYPE_EN,
            _config.CS_SPEC_TYPE_JP,
            _config.CS_SPEC_TYPE_NOREMAKES,
            _config.CS_NONE,
        )

        row = column = 0
        for lt in literals:
            lab = _ttk.Label(self._frame_root, text=lt)
            lab.grid_configure(row=row, column=column)
            row += 1

        row = 0
        column = 1
        var = _config.CFG_TKVAR_SPEC_SEX
        for lt, val in zip(rad_btn_liters, rad_btn_values):
            rad = _ttk.Radiobutton(self._frame_root, text=lt, value=val, variable=var)
            rad.grid_configure(row=row, column=column, sticky=_tk.W)
            self._frame_root.grid_columnconfigure(column, weight=1)
            if (row == 0) and (column == 3):
                row = 1
                column = 1
                var = _config.CFG_TKVAR_SPEC_REMAKES
            else:
                column += 1


class Drawer(CustomWidget):
    MESSAGE_NOT_ITEM_DRAW = "not_item_draw"
    MESSAGE_ALL_ITEMS_DRAWN = "all_items_drawn"

    def __init__(
        self,
        namelist: DrawNameList,
        info_shower: InfoShower,
        default_font: str = GLOBAL_FONT,
        callback: _tp.Optional[_tp.Callable[[], None]] = None,
    ) -> None:
        self._callback = callback
        self._namelist = namelist
        self._info_shower = info_shower
        self._default_font = default_font

        self._start_signal = False
        self._reason = None

    @property
    def not_draw_list(self) -> list[NameInfo]:
        return self._namelist.get_specific_info(
            self._namelist.ITEM_STATE, self._namelist.FLAGS_NOT_DRAWN
        )

    @property
    def reason(self) -> str:
        return self._reason

    def prep_name_info(self) -> list[NameInfo]:
        filtered_list = self.not_draw_list
        print("NOT DRAW LIST:", filtered_list)
        spec_sex, spec_remakes = (
            _config.CFG_TKVAR_SPEC_SEX.get(),
            _config.CFG_TKVAR_SPEC_REMAKES.get(),
        )

        if spec_sex != _config.CS_NONE:
            filter_sex = _partial(
                self._namelist.get_specific_info, DrawNameList.ITEM_SEX
            )
            if spec_sex == _config.CS_SPEC_SEX_MALE:
                filtered_list = filter_sex(DrawNameList.FLAGS_MALE)
            elif spec_sex == _config.CS_SPEC_SEX_FEMALE:
                filtered_list = filter_sex(DrawNameList.FLAGS_FEMALE)

        if spec_remakes != _config.CS_NONE:
            filter_remakes = _partial(
                self._namelist.get_specific_info, DrawNameList.ITEM_REMAKES
            )
            if spec_remakes == _config.CS_SPEC_TYPE_EN:
                filtered_list = filter_remakes(DrawNameList.FLAGS_EN, filtered_list)
            elif spec_remakes == _config.CS_SPEC_TYPE_JP:
                filtered_list = filter_remakes(DrawNameList.FLAGS_JP, filtered_list)
            elif spec_remakes == _config.CS_SPEC_TYPE_NOREMAKES:
                filtered_list = filter_remakes(DrawNameList.FLAGS_NONE, filtered_list)

        return filtered_list

    def can_draw(self, notify: bool = True) -> bool:
        result = True
        if not self._namelist.treeview_items:
            if notify:
                _messagebox.showwarning("警告", "当前无项目可抽取!")
            self._reason = self.MESSAGE_NOT_ITEM_DRAW
            result = False
        elif not self.not_draw_list:
            if notify:
                _messagebox.showwarning("警告", "当前所有项目均已抽取!")
            self._reason = self.MESSAGE_ALL_ITEMS_DRAWN
            result = False

        return result

    def start(self) -> None:
        raise NotImplementedError

    def drawing(self) -> bool:
        return self._start_signal

    def done(self, __name_info: NameInfo, /) -> None:
        self._info_shower.update_state(__name_info)

        if self._callback:
            self._callback()

    def stop(self) -> None:
        if self._start_signal:
            self._start_signal = False

    def set_done_callback(self, __func: _tp.Callable[[], None], /) -> None:
        self._callback = __func


class OneTextDrawer(Drawer):
    def __init__(
        self,
        master: _tk.Misc,
        namelist: DrawNameList,
        info_shower: InfoShower,
        update_interval: int = 20,
        max_interval: int = 1000,
        callback: _tp.Optional[_tp.Callable[[], None]] = None,
    ) -> None:
        super().__init__(namelist, info_shower, callback)
        self._label = self._w = _ttk.Label(
            master, anchor=_tk.CENTER, justify=_tk.CENTER, font=(GLOBAL_FONT, 80)
        )

        self._get_nameinfo = None
        self._update_interval = update_interval
        self._max_update_interval = max_interval

        self._update_interval_2 = 0
        self._max_update_interval_2 = 0

    def nameinfo_generator(
        self,
    ) -> _tp.Generator[_tp.Optional[NameInfo], list[NameInfo], None]:
        name_info_list: list[NameInfo] = yield
        _random.shuffle(name_info_list)

        while True:
            for info in name_info_list:
                if n := (yield info):
                    break
            if n:
                name_info_list = n

            _random.shuffle(name_info_list)

    def update_text(self, __last: bool = False, /) -> None:
        nameinfo = next(self._get_nameinfo)
        self._label.configure(text=nameinfo.name)
        self._label.update_idletasks()
        if __last:
            self.done(nameinfo)

    def draw(self) -> None:
        if not self._start_signal:
            self._update_interval_2 = min(
                self._max_update_interval_2,
                self._update_interval_2
                + _random.randint(self._update_interval, self._update_interval * 4),
            )
            if self._update_interval_2 == self._max_update_interval_2:
                self._label.after(self._max_update_interval, self.update_text, True)
                return None

        if (self._update_interval_2 != self._update_interval) and (self._start_signal):
            self._update_interval_2 = max(
                self._update_interval,
                self._update_interval_2 - _random.randint(2, self._update_interval),
            )

        self.update_text()
        self._label.after(self._update_interval_2, self.draw)

    def start(self) -> bool:
        if (self._start_signal) or (name_info_list := self.not_draw_list):
            self.stop()
            return False

        if not self._get_nameinfo:
            self._get_nameinfo = self.nameinfo_generator()
            next(self._get_nameinfo)

        self._get_nameinfo.send(name_info_list)
        self._start_signal = True
        self._update_interval_2 = self._update_interval * 10
        self._max_update_interval_2 = _random.randint(
            self._update_interval_2 * 2, self._max_update_interval
        )
        self.draw()
        return True


class DiskDrawer(Drawer):
    def __init__(
        self,
        master: _tk.Misc,
        info_shower: InfoShower,
        max_text_size: int,
        default_font: str = GLOBAL_FONT,
        callback: _tp.Optional[_tp.Callable[[], None]] = None,
    ) -> None:
        super().__init__(info_shower.namelist, info_shower, default_font, callback)
        self._canvas = self._w = _tk.Canvas(master=master)

        self._max_text_size = max_text_size
        self._default_font = default_font

        self._canvas_center_position = 0
        self._text_relative_interval = 0.25
        self._canvas_width = self._canvas_height = 0
        self._pointer_x = 0
        self._original_x = 0

        self._showing_items: _deque[DrawItem] = _deque()
        self._hidden_items: _deque[DrawItem] = _deque()

        self._canvas.bind("<Configure>", self._update_canvas_info)
        self._canvas.bind("<ButtonPress-1>", self._mouse_press)
        self._canvas.bind("<ButtonRelease-1>", self._mouse_release)

        self._namelist.register_event_callback(
            DrawNameList.EVENT_LOAD, self.prepare_show_text
        )

    def _compute_text_scaling(self, __text_x: _tp.Union[int, float], /) -> float:
        if self._canvas_center_position == 0:
            self._update_canvas_info()

        if __text_x < self._canvas_center_position:
            font_scaling = __text_x / self._canvas_center_position
        else:
            font_scaling = 1.0 - (
                (__text_x - self._canvas_center_position) / self._canvas_center_position
            )

        return font_scaling

    def _mouse_press(self, event: _tk.Event) -> None:
        self._pointer_x = event.x
        self._original_x = self._canvas.coords("text")[0]

        self._canvas.bind("<Motion>", self._mouse_motion)

    def _mouse_motion(self, event: _tk.Event) -> None:
        self._canvas.moveto("text", self._original_x + (event.x - self._pointer_x))
        self._update_show_text()

    def _mouse_release(self, event: _tk.Event) -> None:
        self._canvas.unbind("<Motion>")
        self._original_x = self._canvas.coords("text")[0]

    def _update_canvas_info(self, _: _tp.Optional[_tk.Event] = None) -> None:
        self._canvas.update_idletasks()
        self._canvas_center_position = self._canvas.winfo_width() // 2
        self._canvas_width = self._canvas.winfo_width()
        self._canvas_height = self._canvas.winfo_height()

    def _update_text_size(
        self,
        __text_id: _tp.Union[int, str],
        __text_x: _tp.Optional[int] = None,
        /,
    ) -> None:
        if not __text_x:
            __text_x = self._canvas.coords(__text_id)[0]

        font_scaling = self._compute_text_scaling(__text_x)
        font_size = int(self._max_text_size * font_scaling)
        self._canvas.itemconfigure(__text_id, font=(self._default_font, font_size))

    def _adjust_text(self, *text_ids: int) -> None:
        if not text_ids:
            text_ids = (i.item_id for i in self._showing_items)

        for i in text_ids:
            self._update_text_size(i)

    def _update_show_text(self) -> None:
        first_text_id, last_text_id = (
            self._showing_items[0][0],
            self._showing_items[-1][0],
        )
        first_text_x, last_text_x = (
            (
                (first_text_real_x := self._canvas.coords(first_text_id)[0])
                + (first_text_real_x / 2)
            ),
            (
                (last_text_real_x := self._canvas.coords(last_text_id)[0])
                - (last_text_real_x / 2)
            ),
        )
        print(first_text_x, last_text_x)
        if first_text_x < 0:
            self._canvas.itemconfigure(first_text_id, state=_tk.HIDDEN)
            deleted_info = self._showing_items.popleft()
            addition_info = self._hidden_items.popleft()
            self._hidden_items.appendleft(deleted_info)
            self._canvas.itemconfigure(addition_info.item_id, state=_tk.NORMAL)
            self._showing_items.append(addition_info)

        if last_text_x > self._canvas_width:
            self._canvas.itemconfigure(last_text_id, state=_tk.HIDDEN)
            deleted_info = self._showing_items.pop()
            addition_info = self._hidden_items.pop()
            self._hidden_items.append(deleted_info)
            self._canvas.itemconfigure(addition_info.item_id, state=_tk.NORMAL)
            self._showing_items.appendleft(addition_info)

        self._adjust_text()

    def prepare_show_text(self) -> None:
        items = [
            DrawItem(
                item_id=self._canvas.create_text(
                    0,
                    self._canvas_height * 0.5,
                    state=_tk.HIDDEN,
                    text=n.name,
                    tags="text",
                ),
                name_info=n,
            )
            for n in self.prep_name_info()
        ]
        self._hidden_items.extend(items)

        text_x_relpos = 0.0
        while text_x_relpos <= 1.0:
            item = self._hidden_items.popleft()
            self._canvas.itemconfigure(item.item_id, state=_tk.NORMAL)
            self._showing_items.append(item)
            self._canvas.moveto(item.item_id, self._canvas_width * text_x_relpos)
            text_x_relpos += self._text_relative_interval

        self._adjust_text()

    def clear_all(self) -> None:
        if items := self._canvas.find_all():
            self._canvas.delete(*items)
        self._showing_items.clear()
        self._hidden_items.clear()


class DrawControl(CustomWidget):
    def __init__(
        self,
        master: _tk.Misc,
        drawer: OneTextDrawer,
        namelist: DrawNameList,
        exit_fn: _tp.Optional[_tp.Callable[[], None]] = None,
    ) -> None:
        drawer.set_done_callback(self._done)
        self._drawer: DiskDrawer = drawer
        self._frame_root = self._w = _ttk.Frame(master)

        btn_literals = ("开始", "重置", "退出")
        btn_commands = (self._start_2, namelist.reset, exit_fn)

        for lt, cmd, idx in zip(btn_literals, btn_commands, range(len(btn_literals))):
            place_kwds = {}
            button_kwds = {}
            if idx == 0:
                button_kwds["default"] = _tk.ACTIVE
            if idx == 1:
                place_kwds["pady"] = 2
            btn = _ttk.Button(
                self._frame_root, text=lt, command=_partial(cmd), **button_kwds
            )
            btn.pack_configure(fill=_tk.BOTH, expand=_tk.YES, **place_kwds)

        _buttons = self._frame_root.winfo_children()
        self._start_button: _ttk.Button = _buttons[0]
        self._reset_button: _ttk.Button = _buttons[1]

    def _start_2(self) -> None:
        self._drawer.prepare_show_text()

    def _start(self) -> None:
        if not self._drawer.drawing():
            if self._drawer.start():
                self._start_button.configure(text="停止")
                self._reset_button.configure(state=_tk.DISABLED)
        else:
            self._stop()

    def _stop(self) -> None:
        self._drawer.stop()
        self._start_button.configure(text="已收到停止命令, 请等待...", state=_tk.DISABLED)

    def _done(self) -> None:
        self._start_button.configure(text="开始", state=_tk.NORMAL)
        self._reset_button.configure(state=_tk.NORMAL)


class Settings(CustomWidget):
    def __init__(self, master: _tk.Misc) -> None:
        self._frame_root = self._w = _ttk.Labelframe(master, text="设置")

        label_literals = ("适应触屏:",)
        rad_btn_literals = ("是", "否")
        rad_btn_values = ("yes", "no")

        row = column = 0
        for lt in label_literals:
            lab = _ttk.Label(self._frame_root, text=lt)
            lab.grid_configure(row=row, column=column)
            row += 1

        row = 0
        column = 1
        var = _config.CFG_TKVAR_SET_ADAPT_SCREEN
        for lt, val in zip(rad_btn_literals, rad_btn_values):
            rad = _ttk.Radiobutton(self._frame_root, text=lt, value=val, variable=var)
            rad.grid_configure(row=row, column=column, sticky=_tk.W)
            self._frame_root.grid_columnconfigure(column, weight=1)
            column += 1


class Control(CustomWidget):
    def __init__(
        self,
        master: _tk.Misc,
        info_shower: InfoShower,
        drawer: Drawer,
        exit_func: _tp.Optional[_tp.Callable[[], None]] = None,
    ) -> None:
        self._frame_root = self._w = _ttk.Frame(master)

        self._draw_options = DrawOptions(self._frame_root)
        self._settings = Settings(self._frame_root)
        self._draw_control = DrawControl(
            self._frame_root, drawer, info_shower._namelist, exit_func
        )

        self._draw_options.frame.place_configure(relwidth=0.7, relheight=0.25)
        self._settings.frame.place_configure(
            relx=1.0, relwidth=0.3, relheight=0.25, anchor=_tk.NE
        )
        self._draw_control.frame.place_configure(
            rely=0.26, relwidth=1.0, relheight=0.74
        )


class Application(_tk.Tk):
    def __init__(self, title: str) -> None:
        """Application Class."""
        super().__init__()
        self.wm_withdraw()
        _TkExMethods.SetWindowPos(window=self, relwidth=0.75, relheight=0.85, rely=0.3)
        self._style = _ttk.Style(self)
        self._style.theme_use("clam")
        self.wm_title(title)
        # self.wm_attributes("-alpha", 0.78)
        self.configure(borderwidth=5)

    def load_config(self) -> None:
        _config.Check()
        _config.Load()

    def exit(self) -> None:
        _config.Save()
        self.quit()
        self.destroy()

    def bulid_gui(self) -> None:
        self._info_shower = InfoShower(self)
        # self._drawer = OneTextDrawer(self, self._info_shower._namelist)
        self._drawer = DiskDrawer(self, self._info_shower, 80)
        self._control_options = Control(
            self, self._info_shower, self._drawer, self.exit
        )

        self._info_shower.frame.place_configure(rely=0.6, relwidth=0.499, relheight=0.4)
        self._drawer.frame.place_configure(relwidth=1.0, relheight=0.6)
        self._control_options.frame.place_configure(
            relx=1.0, rely=0.6, relwidth=0.499, relheight=0.4, anchor=_tk.NE
        )

    def show(self) -> None:
        self.update()
        self.wm_deiconify()
        self.mainloop()
