import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def inline(value):
    tokens = []

    def protect(match):
        tokens.append(match.group())
        return f"ZZTOKEN{len(tokens) - 1}ZZ"

    value = re.sub(r"\$[^$]+\$", protect, value)
    value = value.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
    value = value.replace("†", r"\textsuperscript{\textdagger}")
    value = value.replace("−", "-").replace("–", "--").replace("—", "---")
    value = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", value)
    value = re.sub(r"`([^`]+)`", r"\\texttt{\1}", value)

    def citation(match):
        numbers = match.group(1)
        if "--" in numbers:
            first, last = map(int, numbers.split("--"))
            keys = range(first, last + 1)
        else:
            keys = [int(numbers)]
        return r"\cite{" + ",".join(f"ref{number}" for number in keys) + "}"

    value = re.sub(r"\[(\d+(?:--\d+)?)\]", citation, value)
    for index, token in enumerate(tokens):
        value = value.replace(f"ZZTOKEN{index}ZZ", token)
    return value


def convert(text):
    lines = text.splitlines()
    result = []
    index = 0
    caption = None
    while index < len(lines):
        line = lines[index]
        if line == "$$":
            end = lines.index("$$", index + 1)
            result.extend([r"\[", *lines[index + 1:end], r"\]"])
            index = end + 1
            continue
        if line.startswith("**Table "):
            caption = line[2:-2]
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
                if not all(re.fullmatch(r"[-:]+", cell) for cell in cells):
                    rows.append(cells)
                index += 1
            count = len(rows[0])
            wide = count >= 4 or any(len(cell) > 80 for row in rows for cell in row)
            environment = "table*" if wide else "table"
            if count >= 4:
                widths = [0.40] + [0.60 / (count - 1)] * (count - 1)
            elif count == 3:
                widths = [0.56, 0.22, 0.22]
            else:
                widths = [0.77, 0.23]
            spec = "".join(r">{\raggedright\arraybackslash}p{" + f"{width:.4f}" + r"\tableusable}" for width in widths)
            result.extend([rf"\begin{{{environment}}}[t]", r"\centering", r"\small", r"\setlength{\tabcolsep}{3pt}", r"\renewcommand{\arraystretch}{1.12}"])
            if caption:
                match = re.match(r"Table ([\w()]+)\. (.*)", caption)
                result.extend([r"\renewcommand{\thetable}{" + match.group(1) + "}", r"\caption{" + inline(match.group(2)) + "}"])
            result.extend([r"\setlength{\tableusable}{\dimexpr\linewidth-" + str(2 * count) + r"\tabcolsep\relax}", r"\begin{tabular}{" + spec + "}", r"\toprule"])
            for row_index, row in enumerate(rows):
                result.append(" & ".join(inline(cell) for cell in row) + r" \\")
                if row_index == 0:
                    result.append(r"\midrule")
            result.extend([r"\bottomrule", r"\end{tabular}", rf"\end{{{environment}}}"])
            caption = None
            continue
        heading = re.match(r"(#{2,4}) (.*)", line)
        if heading:
            title = re.sub(r"^(?:\d+(?:\.\d+)*\.?|[A-C]\.\d+)\s+", "", heading.group(2))
            title = re.sub(r"^Appendix [A-C]\. ", "", title)
            command = {2: "section", 3: "subsection", 4: "subsubsection"}[len(heading.group(1))]
            result.append("\\" + command + "{" + inline(title) + "}")
        elif re.match(r"\d+\. ", line):
            result.append(r"\noindent " + inline(line) + r"\par")
        else:
            result.append(inline(line))
        index += 1
    return "\n".join(result) + "\n"


def main():
    source = (ROOT / "georank_en.md").read_text(encoding="utf-8")
    abstract, rest = source.split("## 1. Introduction", 1)
    body, rest = ("## 1. Introduction" + rest).split("## References", 1)
    references, appendix = rest.split("## Appendix A.", 1)
    abstract = abstract.split("## Abstract", 1)[1].strip()
    reference_lines = [r"\begin{thebibliography}{13}"]
    for entry in references.strip().split("\n\n"):
        match = re.match(r"\[(\d+)\] (.+) (https://\S+)$", entry.strip())
        if match:
            reference_lines.append(r"\bibitem{ref" + match.group(1) + "} " + inline(match.group(2)) + r" \href{" + match.group(3) + "}{Online version.}")
    reference_lines.append(r"\end{thebibliography}")
    files = {
        "sec/georank_abstract.tex": "\\begin{abstract}\n" + convert(abstract) + "\\end{abstract}\n",
        "sec/georank_body.tex": convert(body),
        "sec/georank_appendix.tex": "\\appendix\n" + convert("## Appendix A." + appendix),
        "sec/georank_references.tex": "\n".join(reference_lines) + "\n",
    }
    patch = "*** Begin Patch\n"
    for name, contents in files.items():
        relative = "最终论文/论文排版工具/author-kit-CVPR2027-v1-latex/" + name
        patch += "*** Add File: " + relative + "\n"
        patch += "".join("+" + line + "\n" for line in contents.splitlines())
    patch += "*** End Patch"
    print(json.dumps(patch, ensure_ascii=True))


if __name__ == "__main__":
    main()
