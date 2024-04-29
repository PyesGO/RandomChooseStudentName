import json as _json
import os as _os
import tkinter as _tk
import typing as _typing

VAR_OR_STR = _typing.Union[_tk.Variable, str]
_T: _typing.Type[VAR_OR_STR] = VAR_OR_STR

NAME = "config.json"
HOMEPATH = _os.path.abspath(".")
CONFIGPATH = _os.path.join(HOMEPATH, NAME)

CFG_TKVAR_SPEC_SEX: _T = "tkvar_spec_sex"
CFG_TKVAR_SPEC_REMAKES: _T = "tkvar_spec_remakes"
CFG_TKVAR_SET_ADAPT_SCREEN: _T = "tkvar_set_adapt_screen"

CFG_NAMES = "names"
CFG_DRAWN_NAMES = "drawn_names"
CFG_DELETED_NAMES = "deleted_names"

CS_NONE = "none"
CS_SPEC_SEX_MALE = "male"
CS_SPEC_SEX_FEMALE = "female"
CS_SPEC_TYPE_JP = "jp"
CS_SPEC_TYPE_EN = "en"
CS_SPEC_TYPE_NOREMAKES = "no_remakes"

INIT_CONFIG = {
    CFG_TKVAR_SPEC_SEX: "none",
    CFG_TKVAR_SPEC_REMAKES: "none",
    CFG_DRAWN_NAMES: [],
    CFG_DELETED_NAMES: [],
    CFG_NAMES: [],
    CFG_TKVAR_SET_ADAPT_SCREEN: "no",
}


def Init() -> None:
    with open(CONFIGPATH, "wt") as fp:
        fp.write(_json.dumps(INIT_CONFIG))


def ConvertVar(_cfg: dict[str, _typing.Any], /) -> None:
    for k, v in _cfg.copy().items():
        if "tkvar" in k:
            _cfg[k] = _tk.Variable(value=v)


def Load() -> None:
    with open(CONFIGPATH, "rt") as fp:
        conf: dict[str, _typing.Any] = _json.loads(fp.read())
        ConvertVar(conf)
        global_namespace = globals()
        for k, v in conf.items():
            global_namespace["CFG_%s" % k.upper()] = v


def Check() -> None:
    if not _os.path.exists(CONFIGPATH):
        Init()


def Save() -> None:
    name_space = globals()
    cfgs = [i for i in name_space.keys() if i.startswith("CFG")]

    cfg_dict = {}
    for name in cfgs:
        value: _typing.Union[_tk.Variable, _typing.Any] = name_space[name]
        if "TKVAR" in name:
            value = value.get()

        cfg_dict[name.lower()[4:]] = value

    print(cfg_dict)
    with open(CONFIGPATH, "wt", encoding="UTF-8") as fp:
        fp.write(_json.dumps(cfg_dict))
