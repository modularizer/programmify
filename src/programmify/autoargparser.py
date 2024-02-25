import argparse
import functools
import os
import re
import inspect
import sys
from inspect import Parameter
import logging


def autoargparser(func=None, doc_func=None, improve=True, **defaults):
    """Automatically create an argparse parser from a function signature and docstring."""
    if func is None:
        return functools.partial(autoargparser, **defaults)

    hasinit = isinstance(func, type) and hasattr(func, "__init__") and callable(func.__init__)
    doc_func = doc_func if doc_func else func if not hasinit else func.__init__
    call_func = func if not hasinit else func.__init__
    parser = argparse.ArgumentParser()
    docs = inspect.getdoc(doc_func) or ""
    parser.description = docs.splitlines()[0] if docs else ""

    # try to parse the docs for the help of each argument
    lines = [v.strip() for v in docs.split("\n")]
    # for each line in the docstring, get the first a-zA-Z09_ word
    #   name (str): description
    # make a regex to match that, assuming name must be a valid python variable name
    # regesp for azAZ09_ followed by any number of azAZ09_
    doc_matches = {}
    arg_re = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]+)\)\s*:\s*(.*)")
    for line in lines:
        match = arg_re.match(line)
        if match:
            name, typehint, description = match.groups()
            doc_matches[name] = {"typehint": typehint, "description": description}

    params = {}
    collectors = {}
    collect_extras = False
    for name, param in inspect.signature(doc_func).parameters.items():
        if name == "self":
            continue
        d = defaults.get(name, param.default)

        params[name] = d
        # get the typehint
        t = param.annotation
        if t == Parameter.empty:
            t = type(d)
        if t == Parameter.empty:
            t = str

        param_name = name.replace("_", "-")

        # try to parse the docs for the help of each argument
        # find a line that starts with the name of the argument
        help_text = doc_matches.get(name, {}).get("description", param_name.title())

        required = d == Parameter.empty and param.kind == Parameter.POSITIONAL_ONLY
        flag = t == bool

        if required:
            # if this is a var collector, use nargs="*"
            if param.kind == Parameter.VAR_POSITIONAL:
                parser.add_argument(f"{param_name}", nargs="*", type=t, default=(), help=help_text)
                collectors["args"] = name
            else:
                parser.add_argument(f"{param_name}", type=t, help=help_text)
        elif flag:
            if not d:
                parser.add_argument(f"--{param_name}", action="store_true", help=help_text)
            else:
                parser.add_argument(f"--no-{param_name}", action="store_false", help=help_text, dest=name)
        else:
            # if this is a var collector of keyword args,
            if param.kind == Parameter.VAR_KEYWORD:
                collect_extras = name
                collectors["kwargs"] = name
                parser.add_argument(f"--{param_name}", type=t, default=None, help=help_text, nargs=argparse.REMAINDER)
            else:
                parser.add_argument(f"--{param_name}", type=t, default=d, help=help_text)

    extra_params = set()

    if improve:
        if "quiet" not in params:
            extra_params.add("quiet")
            parser.add_argument("--quiet", action="store_true", help="Suppress output")
        for level in logging._nameToLevel:
            if level.lower() not in params:
                extra_params.add(level.lower())
                parser.add_argument(f"--{level.lower()}", action="store_true", help=f"Set logging level to {level}")

    def cli(*args, **kwargs):
        if collect_extras:
            extras = [k.strip("-") for k in sys.argv[1:] if k.startswith("-")  (k not in params) and (k not in ["-h", "--help"])]
            for k in extras:
                parser.add_argument(f"--{k}", type=str, default=None, help=f"goes to {collect_extras}")
        parser_args = parser.parse_args()
        # check for help
        if "help" in parser_args:
            print("help")
            parser.print_help()
            return
        parser_kwargs = vars(parser_args)
        kwargs = {**{k: v for k, v in parser_kwargs.items() if k not in extra_params}, **kwargs}
        if "args" in collectors:
            cargs = kwargs.pop(collectors["args"])
            if cargs:
                args = (*args, *cargs)
        if "kwargs" in collectors:
            ckwargs = kwargs.pop(collectors["kwargs"])
            if ckwargs:
                kwargs = {**ckwargs, **kwargs}

        # now remove the kwargs for params included in *args
        sig_params = inspect.signature(call_func).parameters
        for i in range(len(args)):
            if i >= len(sig_params):
                break
            name = list(sig_params.keys())[i]
            param = sig_params[name]
            if param.kind == Parameter.VAR_POSITIONAL:
                break
            if name in kwargs:
                del kwargs[name]

        if parser_kwargs.get("quiet", False):
            print("Suppressing output")
            # redirect stdout and stderr
            with open(os.devnull, "w") as f:
                sys.stdout = f
                sys.stderr = f
                r = call_func(*args, **kwargs)
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                if r is not None:
                    print(r)
                return

        # set the logging level
        log_level = None
        for name in extra_params:
            if name in parser_kwargs and parser_kwargs[name]:
                log_level = name
                break
        if log_level:
            logging.basicConfig(level=log_level.upper())


        # call the function with the parsed args
        r = call_func(*args, **kwargs)
        if r is not None:
            print(r)
        return r

    if hasinit:
        func.__init__ = cli
        return func

    return cli

