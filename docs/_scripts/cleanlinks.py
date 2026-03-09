from difflib import SequenceMatcher
import json
from pathlib import Path
import os
import sys

import click
import requests


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


def recursive_search_and_save(fixes, directory, dry_run):
    files_updated = set()
    if len(fixes) == 0:
        return

    click.secho(f"Scanning {str(directory)} for links to update...", fg="blue")
    for root, _dirs, files in directory.walk():
        for file in files:
            try:
                curr_file = root / file
                if curr_file.suffix not in (".rst", ".py"):
                    continue

                click.secho(".", fg="blue", nl=False)

                with curr_file.open("r") as f:
                    text = f.read()

                # search for other instances of the URL in other files and replace them as well
                for original_link, new_link in fixes.items():
                    if original_link not in text:
                        continue

                    click.secho(f"{os.linesep}{curr_file}", fg="blue")
                    click.secho(
                        f"  {original_link} -> {new_link}",
                        fg="green",
                    )

                    if not dry_run:
                        # Replace the link in the text
                        text = text.replace(original_link, new_link)

                        # Save changes to the file
                        with curr_file.open("w") as f:
                            f.write(text)
                        click.echo(f"  {click.style('Changes saved!', fg="green")}")
                    else:
                        click.echo(
                            f"  {click.style('Dry Run:', bg="yellow")} Changes NOT saved."
                        )

                    files_updated.add(str(curr_file))
            except Exception as e:
                click.secho(
                    f"ERROR: an unexpected error occurred while replacing links in {str(file)}: {e}",
                    fg="red",
                )
                click.secho("       Skipping file...", fg="red")

    click.secho(
        f"{os.linesep}Fixed {len(fixes)} links in {len(files_updated)} files.",
        fg="green",
    )


def fix_links(links_type, links, docs_dir):
    fixes = dict()
    ctx = click.get_current_context()
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
        return fixes

    # Prompt user if they want to review each link
    if links_type == "broken":
        # User must review each broken link, bc there is no way to know what the correct link is
        review_each = True
    elif links_type == "redirected":
        review_each = click.prompt(
            click.style(
                f"Would you like to review each {links_type} fix [r] or fix automatically [a]?",
                fg="magenta",
            ),
            default="r",
        )
        review_each = review_each.lower() == "r"

    click.secho(f"{os.linesep}Fixing {links_type} links...", bg="magenta")
    files = group_by_file(links)
    with click.progressbar(
        length=len(links), label=f"Fixing {links_type} links"
    ) as progress_bar:
        for filename, file_links in files.items():
            file_links = files[filename]
            click.secho(os.linesep)
            click.secho(f"{filename}", bg="blue")
            try:
                with open(docs_dir / filename, "r") as f:
                    lines = f.readlines()
            except Exception as e:
                click.secho(
                    f"ERROR: an unexpected error occurred while reading lines in {str(filename)}: {e}",
                    fg="red",
                )
                click.secho("       Skipping file...", fg="red")
                continue

            # Replace each link in the file
            for link in file_links:
                original_link = link["uri"]
                new_link = link["info"] if links_type == "redirected" else ""
                if links_type == "broken":
                    click.echo(
                        f"{os.linesep}  {click.style(original_link, bg="magenta")}"
                    )
                elif links_type == "redirected":
                    click.echo(
                        f"{os.linesep}  {click.style(link["code"], bold=True)}: {click.style(original_link, bg="magenta")} -> {click.style(new_link, bg="magenta")}"
                    )

                try:
                    line_idx = link["lineno"] - 1
                    try:
                        line = lines[line_idx].strip()
                    except IndexError:
                        line = "WARNING: The line can't be found in RST file, probably in a Python docstring."

                    # Compute the similarity between the original and new link
                    similarity = calculate_similarity(original_link, new_link)
                    too_dissimilar = similarity <= similarity_threshold

                    # Handle cases when user input is required
                    if review_each or too_dissimilar:
                        click.echo(
                            f"  {click.style(link['lineno'], bold=True)}: {line}"
                        )
                        if links_type == "broken":
                            click.echo(
                                f'  {click.style('Info', bold=True)}: {link["info"]}'
                            )

                        if not review_each and too_dissimilar:
                            click.echo(
                                f"  {click.style('Review Required', bold=True, fg="yellow")}: The new link is significantly different from the original."
                            )

                        valid = False
                        was_skipped = False
                        while not valid:
                            if links_type == "broken":
                                entered_option = click.prompt(
                                    click.style(
                                        f"  Please chose one of the following options:{os.linesep}"
                                        f"    [1] Keep Original: {original_link}{os.linesep}"
                                        f"    [2] Skip{os.linesep}"
                                        f"    [9] Exit and Save{os.linesep}"
                                        f"    [-] Enter new:{os.linesep}   ",
                                        fg="magenta",
                                    ),
                                    default="1",
                                )
                            elif links_type == "redirected":
                                entered_option = click.prompt(
                                    click.style(
                                        f"  Please chose one of the following options:{os.linesep}"
                                        f"    [0] Use Redirected: {new_link}{os.linesep}"
                                        f"    [1] Keep Original:  {original_link}{os.linesep}"
                                        f"    [2] Skip{os.linesep}"
                                        f"    [9] Exit and Save{os.linesep}"
                                        f"    [-] Enter new:{os.linesep}   ",
                                        fg="magenta",
                                    ),
                                    default="0",
                                )

                            # Evaluate the user input
                            if links_type == "redirected" and entered_option == "0":
                                new_link = new_link
                            elif entered_option == "1":
                                new_link = original_link
                            elif entered_option == "2":
                                click.echo(f"  {click.style('Skipped', bg="yellow")}")
                                link["unfixed_reason"] = "User skipped."
                                progress_bar.update(1)
                                click.secho(os.linesep)
                                was_skipped = True
                                break
                            elif entered_option == "9":
                                click.secho(f"Exiting {links_type}...", fg="yellow")
                                return fixes
                            else:
                                # User supplied a new link
                                new_link = entered_option

                            # Validate the new link
                            try:
                                click.secho(
                                    f"  Validating supplied URL: {new_link}...",
                                    fg="blue",
                                )
                                response = requests.get(new_link, timeout=10)
                                if (
                                    not 200 >= response.status_code < 300
                                    and response.status_code not in [403, 406]
                                ):
                                    click.secho(
                                        f"  Error: URL returned status code {response.status_code}.",
                                        fg="red",
                                    )
                                    click.secho("  Please enter a valid URL.", fg="red")
                                    new_link = (
                                        link["info"]
                                        if links_type == "redirected"
                                        else ""
                                    )
                                    continue
                            except requests.RequestException as e:
                                click.secho(f"  Error: {e}", fg="red")
                                click.secho("  Please enter a valid URL.", fg="red")
                                new_link = (
                                    link["info"] if links_type == "redirected" else ""
                                )
                                continue

                            click.secho("  URL is valid.", fg="green")
                            valid = True

                        if was_skipped:
                            continue

                        if not new_link:
                            click.echo(f"  {click.style('Skipped', bg="yellow")}")
                            link["unfixed_reason"] = "No link provided."
                            progress_bar.update(1)
                            click.secho(os.linesep)
                            continue

                        if original_link == new_link:
                            click.echo(
                                f"  {click.style('No Change:', bg="yellow")} {new_link}"
                            )
                            continue
                        else:
                            click.echo(
                                f"  {click.style('Fix:', bg="green")} {original_link} -> {new_link}"
                            )

                    # Save to fixes dict
                    if original_link not in fixes:
                        fixes[original_link] = new_link
                    else:
                        click.secho(
                            f"    WARNING: Multiple fixes found for the same original link: {original_link}",
                            fg="yellow",
                        )

                except click.Abort:
                    # Propagate Abort to kill the script on Keyboard interrupt
                    raise
                except IndexError:
                    link["unfixed_reason"] = "Could not find line."
                    click.secho("ERROR: Could not find line.", fg="red")
                except Exception as e:
                    link["unfixed_reason"] = f"Unexpected error occurred: {str(e)}"
                    click.secho(f"ERROR: {e}", fg="red")

                progress_bar.update(1)
                click.secho(os.linesep)

    return fixes


@click.command()
@click.option(
    "-d", "--dry-run", "dry_run", is_flag=True, help="Do not make any changes."
)
@click.option(
    "-s",
    "--similarity",
    "similarity_threshold",
    type=float,
    default=0.8,
    help="Similarity threshold used to determine if user input is required in automatic redirect fixes. Value between 0 and 1.",
)
def clean_links(dry_run, similarity_threshold):
    """Clean up the links in the documentation."""
    if dry_run:
        click.secho(
            "Dry Run: No changes will be saved.",
            fg="yellow",
        )

    # Parse the linkcheck output
    docs_dir = Path(__file__).parents[1]
    project_root = docs_dir.parents[0]
    links, files = parse_linkcheck_output(docs_dir)
    redirect_fixes = list()
    broken_fixes = list()

    # Fix Redirected Links
    if len(links["redirected"]) > 0:
        redirect_fixes = fix_links("redirected", links["redirected"], docs_dir)
        recursive_search_and_save(redirect_fixes, project_root, dry_run)
    else:
        click.secho(
            f"{os.linesep}Good news! No redirected links to fix.",
            fg="green",
        )

    # Fix Broken Links
    if len(links["broken"]) > 0:
        broken_fixes = fix_links("broken", links["broken"], docs_dir)
        recursive_search_and_save(broken_fixes, project_root, dry_run)
    else:
        click.secho(
            f"{os.linesep}Good news! No redirected links to fix.",
            fg="green",
        )

    # Summary Report
    redirect_fixed = len(redirect_fixes)
    broken_fixed = len(broken_fixes)
    click.secho(f"{os.linesep}Link Check Summary:", fg="blue")
    click.echo(f"  Broken: {broken_fixed}/{len(links['broken'])}")
    click.echo(f"  Redirected: {redirect_fixed}/{len(links['redirected'])}")
    click.echo(f"  Working: {len(links['working'])}")
    click.echo(f"  Ignored: {len(links['ignored'])}")
    click.echo(f"  Timeout: {len(links['timeout'])}")
    click.echo(f"  Other: {len(links['other'])}")
    click.echo(f"  Total: {sum([len(links[key]) for key in links])}")
    click.echo(f"  Files: {len(files)}")

    # Warning
    click.secho("WARNING: Please review the changes before committing.", fg="yellow")


if __name__ == "__main__":
    clean_links()
