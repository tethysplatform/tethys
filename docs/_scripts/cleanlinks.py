from difflib import SequenceMatcher
import copy
import json
from pathlib import Path
import os
import sys

import click


def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def group_by_file(links):
    files = {}
    for link in links:
        if link["filename"] not in files:
            files[link["filename"]] = []
        files[link["filename"]].append(link)
    return files


def parse_linkcheck_output(docs_dir):
    build_dir = docs_dir / "_build"
    linkcheck_dir = build_dir / "linkcheck"
    linkcheck_out = linkcheck_dir / "output.json"

    if (
        not build_dir.exists()
        or not linkcheck_dir.exists()
        or not linkcheck_out.exists()
    ):
        click.secho("ERROR: Could not find linkcheck output (output.json).", fg="red")
        click.secho(
            '       Please, run "make linkcheck" first and try again.', fg="red"
        )
        sys.exit(1)

    click.echo(f"Using linkcheck output at {click.style(linkcheck_out, fg="blue")}")

    # Parse the linkcheck output
    with linkcheck_out.open() as f:
        lines = f.readlines()

    links = {
        "broken": [],
        "timeout": [],
        "redirected": [],
        "ignored": [],
        "working": [],
        "other": [],
    }
    files = set()

    for line in lines:
        data = json.loads(line)
        if data["status"] == "broken" or data["status"] == "timeout":
            links["broken"].append(data)
        elif data["status"] == "redirected":
            links["redirected"].append(data)
        elif data["status"] == "ignored" or data["status"] == "unchecked":
            links["ignored"].append(data)
        elif data["status"] == "working":
            links["working"].append(data)
        else:
            links["other"].append(data)
        files.add(data["filename"])

    return links, files


def fix_links(links_type, links, docs_dir):
    ctx = click.get_current_context()
    dry_run = ctx.params["dry_run"]
    similarity_threshold = ctx.params["similarity_threshold"]

    if links_type not in ["broken", "redirected"]:
        raise ValueError(f"Invalid links type: {links_type}")

    # Prompt user if they want to fix the links
    should_fix = click.prompt(
        click.style(
            f"{os.linesep}Would you like to fix {len(links)} {links_type} links? [y/n]",
            fg="magenta",
        ),
        default="y",
    )
    if should_fix.lower() == "n":
        return copy.deepcopy(links)

    # Prompt user if they want to review each link
    if links_type == "broken":
        # User must review each broken link, bc there is no way to know what the correct link is
        review_each = True
    elif links_type == "redirected":
        review_each = click.prompt(
            # TODO: automatic: fix only the links that are very different (long or different domain)
            click.style(
                f"Would you like to review each {links_type} fix [r] or fix automatically [a]?",
                fg="magenta",
            ),
            default="r",
        )
        review_each = review_each.lower() == "r"

    click.secho(f"{os.linesep}Fixing {links_type} links...", bg="magenta")
    not_fixed = []

    files = group_by_file(links)
    with click.progressbar(
        length=len(links), label=f"Fixing {links_type} links"
    ) as progress_bar:
        for filename, file_links in files.items():
            file_links = files[filename]
            click.secho(f"{os.linesep}{filename}", fg="blue")
            with open(docs_dir / filename, "r") as f:
                lines = f.readlines()

            # Replace each link in the file
            for link in file_links:
                original_link = link["uri"]
                new_link = link["info"] if links_type == "redirected" else ""
                if links_type == "broken":
                    click.echo(
                        f"{os.linesep}  {click.style(link['lineno'], bold=True)}: {click.style(original_link, bg="magenta")}"
                    )
                elif links_type == "redirected":
                    click.echo(
                        f"{os.linesep}  {click.style(link['lineno'], bold=True)}: {click.style(original_link, bg="magenta")} -> {click.style(new_link, bg="magenta")}"
                    )

                try:
                    line_idx = link["lineno"] - 1
                    line = lines[line_idx].strip()

                    # Check if the link is in the line
                    found = line.find(original_link)
                    if not found:
                        click.secho(
                            "WARNING: Could not find link to replace in line:",
                            fg="yellow",
                        )
                        click.echo(f"         {link["lineno"]}: {lines[line_idx]}")
                        not_fixed.append(link)
                        progress_bar.update(1)
                        continue

                    # Compute the similarity between the original and new link
                    similarity = calculate_similarity(original_link, new_link)
                    too_dissimilar = similarity <= similarity_threshold

                    # Replace the link
                    if review_each or too_dissimilar:
                        click.echo(f"  {click.style('Line', bold=True)}: {line}")
                        if links_type == "broken":
                            click.echo(
                                f'  {click.style('Info', bold=True)}: {link["info"]}'
                            )
                        elif links_type == "redirected":
                            click.echo(
                                f'  {click.style('Code', bold=True)}: {link["code"]}'
                            )

                        if not review_each and too_dissimilar:
                            click.echo(
                                f"  {click.style('Review Required', bold=True, fg="yellow")}: The new link is very different from the original."
                            )

                        if links_type == "broken":
                            new_link = click.prompt(
                                click.style(
                                    "  Please enter new URL or press Enter to skip",
                                    fg="magenta",
                                ),
                                default=new_link,
                            )
                        elif links_type == "redirected":
                            new_link = click.prompt(
                                click.style(
                                    "  Please enter new URL or press Enter to accept the default",
                                    fg="magenta",
                                ),
                                default=new_link,
                            )

                        if not new_link:
                            click.secho("  Skipped", fg="yellow")
                            not_fixed.append(link)

                    click.secho(
                        f"  Replacing: {original_link} -> {new_link}", fg="green"
                    )
                    lines[line_idx] = lines[line_idx].replace(original_link, new_link)

                except click.Abort:
                    # Propagate Abort to kill the script on Keyboard interrupt
                    raise
                except IndexError:
                    click.secho("ERROR: Could not find line.", fg="red")
                except Exception as e:
                    click.echo(type(e))
                    click.secho(f"ERROR: {e}", fg="red")

                progress_bar.update(1)

            if not dry_run:
                with open(docs_dir / filename, "w") as f:
                    f.writelines(lines)

    return not_fixed


@click.command()
@click.option(
    "-dry", "--dry-run", "dry_run", is_flag=True, help="Do not make any changes."
)
@click.option(
    "-s",
    "--similarity",
    "similarity_threshold",
    type=float,
    default=0.8,
    help="Similarity threshold used to determine if user input is required in automatic redirect fixes.",
)
def clean_links(dry_run, similarity_threshold):
    """Clean up the links in the documentation."""
    # Parse the linkcheck output
    docs_dir = Path(__file__).parents[1]
    links, files = parse_linkcheck_output(docs_dir)

    # Fix Redirected Links
    redirect_not_fixed = fix_links("redirected", links["redirected"], docs_dir)

    # Fix Broken Links
    broken_not_fixed = fix_links("broken", links["broken"], docs_dir)

    # Summary Report
    broken_fixed = len(links["broken"]) - len(broken_not_fixed)
    redirect_fixed = len(links["redirected"]) - len(redirect_not_fixed)
    click.secho("Link Check Summary:", fg="blue")
    click.echo(f"  Broken: {broken_fixed}/{len(links['broken'])}")
    click.echo(f"  Redirected: {redirect_fixed}/{len(links['redirected'])}")
    click.echo(f"  Working: {len(links['working'])}")
    click.echo(f"  Ignored: {len(links['ignored'])}")
    click.echo(f"  Timeout: {len(links['timeout'])}")
    click.echo(f"  Other: {len(links['other'])}")
    click.echo(f"  Total: {len(links)}")
    click.echo(f"  Files: {len(files)}")

    # TODO: Skipped/not fixed Report


if __name__ == "__main__":
    clean_links()
