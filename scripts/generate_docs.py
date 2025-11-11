from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class ArgumentInfo:
    name: str
    default: Optional[str] = None
    annotation: Optional[str] = None
    kind: str = "positional"


@dataclass
class FunctionInfo:
    name: str
    signature: str
    docstring: str | None
    args: List[ArgumentInfo] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    docstring: str | None
    methods: List[FunctionInfo] = field(default_factory=list)


@dataclass
class ModuleDocs:
    path: Path
    module_docstring: str | None
    functions: List[FunctionInfo]
    classes: List[ClassInfo]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate markdown documentation for Python modules."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Files or directories to document.",
    )
    parser.add_argument(
        "--output-dir",
        default="docs",
        help="Directory to place generated documentation (default: docs).",
    )
    return parser.parse_args()


def iter_python_files(paths: Iterable[str]) -> Iterable[Path]:
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            for file in sorted(path.rglob("*.py")):
                if file.name == "__init__.py":
                    continue
                yield file.resolve()
        elif path.suffix == ".py":
            yield path.resolve()


def format_default(value: ast.expr) -> str:
    try:
        return ast.unparse(value)
    except Exception:
        return "<complex default>"


def format_annotation(annotation: ast.expr | None) -> Optional[str]:
    if annotation is None:
        return None
    try:
        return ast.unparse(annotation)
    except Exception:
        return "<complex annotation>"


def collect_arguments(node: ast.FunctionDef) -> List[ArgumentInfo]:
    result: List[ArgumentInfo] = []
    args = node.args

    positional_all = list(args.posonlyargs) + list(args.args)
    defaults = [None] * (len(positional_all) - len(args.defaults)) + list(args.defaults)

    for arg, default in zip(positional_all, defaults):
        kind = "positional-only" if arg in args.posonlyargs else "positional"
        result.append(
            ArgumentInfo(
                name=arg.arg,
                default=format_default(default) if default is not None else None,
                annotation=format_annotation(arg.annotation),
                kind=kind,
            )
        )

    # marker for position-only arguments termination
    if args.posonlyargs:
        result.append(ArgumentInfo(name="/", kind="separator"))

    if args.vararg:
        result.append(
            ArgumentInfo(
                name=f"*{args.vararg.arg}",
                annotation=format_annotation(args.vararg.annotation),
                kind="vararg",
            )
        )

    elif args.kwonlyargs:
        # bare * separator when keyword-only arguments exist without *args
        result.append(ArgumentInfo(name="*", kind="separator"))

    kwonly_defaults = {
        kw.arg: default for kw, default in zip(args.kwonlyargs, args.kw_defaults)
    }

    for kw in args.kwonlyargs:
        result.append(
            ArgumentInfo(
                name=kw.arg,
                default=format_default(kwonly_defaults.get(kw.arg))
                if kwonly_defaults.get(kw.arg) is not None
                else None,
                annotation=format_annotation(kw.annotation),
                kind="keyword-only",
            )
        )

    if args.kwarg:
        result.append(
            ArgumentInfo(
                name=f"**{args.kwarg.arg}",
                annotation=format_annotation(args.kwarg.annotation),
                kind="varkw",
            )
        )

    return result


def build_signature(node: ast.FunctionDef, arguments: List[ArgumentInfo]) -> str:
    rendered_parts: List[str] = []
    for arg in arguments:
        if arg.kind == "separator":
            rendered_parts.append(arg.name)
            continue

        text = arg.name
        if arg.annotation and not arg.name.startswith("*"):
            text = f"{text}: {arg.annotation}"
        elif arg.annotation and arg.name.startswith("*"):
            text = f"{arg.name}: {arg.annotation}"
        if arg.default is not None and arg.kind != "vararg" and arg.kind != "varkw":
            text = f"{text}={arg.default}"
        rendered_parts.append(text)

    joined = ", ".join(rendered_parts)
    return f"{node.name}({joined})"


def collect_function(node: ast.FunctionDef) -> FunctionInfo:
    arguments = collect_arguments(node)
    return FunctionInfo(
        name=node.name,
        signature=build_signature(node, arguments),
        docstring=ast.get_docstring(node),
        args=arguments,
    )


def collect_module(path: Path) -> ModuleDocs:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions: List[FunctionInfo] = []
    classes: List[ClassInfo] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(collect_function(node))
        elif isinstance(node, ast.ClassDef):
            methods = [
                collect_function(child)
                for child in node.body
                if isinstance(child, ast.FunctionDef)
            ]
            classes.append(
                ClassInfo(
                    name=node.name,
                    docstring=ast.get_docstring(node),
                    methods=methods,
                )
            )

    return ModuleDocs(
        path=path,
        module_docstring=ast.get_docstring(tree),
        functions=functions,
        classes=classes,
    )


def format_docstring(doc: Optional[str]) -> str:
    return doc.strip() if doc else "No description provided."


def render_argument(arg: ArgumentInfo) -> Optional[str]:
    if arg.kind == "separator":
        return None

    parts = [f"`{arg.name}`"]
    if arg.annotation:
        parts.append(f": `{arg.annotation}`")
    if arg.default is not None:
        parts.append(f"(default: `{arg.default}`)")
    if arg.kind in {"vararg", "varkw"}:
        parts.append(f"[{arg.kind}]")
    if arg.kind == "keyword-only":
        parts.append("[keyword-only]")
    return " ".join(parts)


def render_module_docs(docs: ModuleDocs, root: Path, output_dir: Path) -> None:
    relative = docs.path.relative_to(root)
    output_path = output_dir / relative.with_suffix(".md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append(f"# Module `{relative.as_posix()}`")
    lines.append("")
    if docs.module_docstring:
        lines.append(format_docstring(docs.module_docstring))
        lines.append("")

    if docs.functions:
        lines.append("## Functions")
        lines.append("")
        for func in docs.functions:
            lines.append(f"### `{func.signature}`")
            lines.append("")
            lines.append(format_docstring(func.docstring))
            lines.append("")
            if func.args:
                lines.append("**Arguments:**")
                for arg in func.args:
                    rendered = render_argument(arg)
                    if rendered:
                        lines.append(f"- {rendered}")
                lines.append("")

    if docs.classes:
        lines.append("## Classes")
        lines.append("")
        for cls in docs.classes:
            lines.append(f"### `{cls.name}`")
            lines.append("")
            lines.append(format_docstring(cls.docstring))
            lines.append("")
            if cls.methods:
                lines.append("#### Methods")
                lines.append("")
                for method in cls.methods:
                    lines.append(f"- `{method.signature}`")
                    lines.append(f"  - {format_docstring(method.docstring)}")
                    if method.args:
                        lines.append("  - Arguments:")
                        for arg in method.args:
                            rendered = render_argument(arg)
                            if rendered:
                                lines.append(f"    - {rendered}")
                    lines.append("")

    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path.cwd()
    output_dir = Path(args.output_dir)

    for path in iter_python_files(args.paths):
        docs = collect_module(path)
        render_module_docs(docs, root=root, output_dir=output_dir)


if __name__ == "__main__":
    main()

