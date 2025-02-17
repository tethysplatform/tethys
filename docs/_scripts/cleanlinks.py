from difflib import SequenceMatcher
import copy
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
            click.secho(os.linesep)
            click.secho(f"{filename}", bg="blue")
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
                    original_found = line.find(original_link)
                    if not original_found:
                        # Check for links that were already fixed in a previous session and skip them
                        if links_type == "redirected":
                            new_found = link.find(new_link)
                            if new_found:
                                link["unfixed_reason"] = "ALREADY_FIXED"
                                not_fixed.append(link)
                                progress_bar.update(1)
                                click.secho(os.linesep)
                                continue

                        click.secho(
                            "WARNING: Could not find link to replace in line:",
                            fg="yellow",
                        )
                        click.echo(f"         {link["lineno"]}: {lines[line_idx]}")
                        link["unfixed_reason"] = "Link not found in line."
                        not_fixed.append(link)
                        progress_bar.update(1)
                        click.secho(os.linesep)
                        continue

                    # Compute the similarity between the original and new link
                    similarity = calculate_similarity(original_link, new_link)
                    too_dissimilar = similarity <= similarity_threshold

                    # Handle cases when user input is required
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
                                        f"    [1] Keep Original: {original_link}{os.linesep}"
                                        f"    [2] Skip{os.linesep}"
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
                                not_fixed.append(link)
                                progress_bar.update(1)
                                click.secho(os.linesep)
                                was_skipped = True
                                break
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
                                if response.status_code != 200:
                                    click.secho(
                                        f"  Error: URL returned status code {response.status_code}.",
                                        fg="red",
                                    )
                                    click.secho(
                                        "  Please enter a valid URL.", fg="red"
                                    )
                                    continue
                            except requests.RequestException as e:
                                click.secho(f"  Error: {e}", fg="red")
                                click.secho("  Please enter a valid URL.", fg="red")
                                continue

                            click.secho("  URL is valid.", fg="green")
                            valid = True

                        if was_skipped:
                            continue

                        if not new_link:
                            click.echo(f"  {click.style('Skipped', bg="yellow")}")
                            link["unfixed_reason"] = "No link provided."
                            not_fixed.append(link)
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
                                f"  {click.style('Replacing:', bg="green")} {original_link} -> {new_link}"
                            )

                    # TODO: Refactor how replacing happens
                    # Save to dict and then do project-wide find and replace on rst and python files?
                    lines[line_idx] = lines[line_idx].replace(original_link, new_link)
                    if new_link not in lines[line_idx]:
                        link["unfixed_reason"] = (
                            "Link could not be updated - doc string?"
                        )
                        not_fixed.append(link)
                        click.secho(
                            "    WARNING: Could not replace link, is it in a doc string?",
                            fg="yellow",
                        )

                except click.Abort:
                    # Propagate Abort to kill the script on Keyboard interrupt
                    raise
                except IndexError:
                    link["unfixed_reason"] = "Could not find line."
                    not_fixed.append(link)
                    click.secho("ERROR: Could not find line.", fg="red")
                except Exception as e:
                    link["unfixed_reason"] = f"Unexpected error occurred: {str(e)}"
                    not_fixed.append(link)
                    click.secho(f"ERROR: {e}", fg="red")

                progress_bar.update(1)
                click.secho(os.linesep)

            if not dry_run:
                with open(docs_dir / filename, "w") as f:
                    f.writelines(lines)

    return not_fixed


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
    # Parse the linkcheck output
    docs_dir = Path(__file__).parents[1]
    links, files = parse_linkcheck_output(docs_dir)

    # Fix Redirected Links
    redirect_not_fixed = fix_links("redirected", links["redirected"], docs_dir)

    # Fix Broken Links
    broken_not_fixed = fix_links("broken", links["broken"], docs_dir)

    # Skipped/Fixed Report
    # click.secho(f"{os.linesep}Skipped / Unfixed Links:", fg="blue")
    # # TODO: decided what to print: skipped? ignored? already fixed?
    # for link in broken_not_fixed:
    #     click.echo(f"  Broken: {link['uri']}")
    #     click.echo(f"    Reason: {link.get('unfixed_reason', 'Skipped')}")

    # for link in redirect_not_fixed:
    #     click.echo(f"  Redirected: {link['uri']} -> {link['info']}")
    #     click.echo(f"    Reason: {link.get('unfixed_reason', 'Skipped')}")

    # Summary Report
    broken_fixed = len(links["broken"]) - len(broken_not_fixed)
    redirect_fixed = len(links["redirected"]) - len(redirect_not_fixed)
    click.secho(f"{os.linesep}Link Check Summary:", fg="blue")
    click.echo(f"  Broken: {broken_fixed}/{len(links['broken'])}")
    click.echo(f"  Redirected: {redirect_fixed}/{len(links['redirected'])}")
    click.echo(f"  Working: {len(links['working'])}")
    click.echo(f"  Ignored: {len(links['ignored'])}")
    click.echo(f"  Timeout: {len(links['timeout'])}")
    click.echo(f"  Other: {len(links['other'])}")
    click.echo(f"  Total: {len(links)}")
    click.echo(f"  Files: {len(files)}")

    # Warning
    click.secho("WARNING: Please review the changes before committing.", fg="yellow")


if __name__ == "__main__":
    clean_links()
