from difflib import SequenceMatcher
import copy
import json
from pathlib import Path
import os
import re
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


def review_spell_check_output(docs_dir):
    build_dir = docs_dir / "_build"
    spelling_dir = build_dir / "spelling"

    if (
        not build_dir.exists()
        or not spelling_dir.exists()
    ):
        click.secho("ERROR: Could not find spelling output.", fg="red")
        click.secho(
            '       Please, run "make spelling" first and try again.', fg="red"
        )
        sys.exit(1)

    click.echo(f"Using spelling output at {click.style(spelling_dir, fg="blue")}")
    
    reg = re.compile(
        r"^(?P<file>.*):(?P<line_no>\d+|None): \((?P<word>.+)\) (?P<suggestions>\[.+\])* (?P<line>.+)$"
    )
    
    errors = 0
    total = 0
    fixes = dict()
    for root, _dirs, files in spelling_dir.walk():
        for file in files:
            # Skip the stupid _static file
            if file in ["_static"]:
                continue

            try:
                # /<path_to>/tethys/docs/_build/spelling/index.spelling
                curr_file = root / file
                with curr_file.open('r') as f:
                    spelling_errors = f.readlines()

                for spelling_error in spelling_errors:
                    total += 1
                    ret = reg.match(spelling_error)
                    if not ret:
                        click.secho(f"ERROR: Could not parse spelling error:", fg="red")
                        click.secho(f"       {spelling_error}", fg="red")
                        errors += 1
                        input("Press Enter to continue...")
                        continue

                    # /<path_to>/tethys/docs/index.rst 
                    source_file = docs_dir / ret.group("file")
                    # Line containing the misspelled word
                    line_no = ret.group("line_no")
                    line = ret.group("line")
                    misspelled_word = ret.group("word")
                    word_suggestions = ret.group("suggestions")

                    click.secho(f"{str(source_file)}", bg="blue")

                    if word_suggestions:
                        try:
                            word_suggestions = json.loads(word_suggestions)
                        except json.JSONDecodeError:
                            click.secho(f"WARNING: Could not parse suggestions: {word_suggestions}", fg="yellow")
                            word_suggestions = []
                    click.echo(f"  {line_no}: {line}")
                    click.secho(f"  {misspelled_word}", fg="red")
                    
                    if misspelled_word in fixes:
                        fixes[misspelled_word]["files"].append({
                            "filename": source_file,
                            "lineno": line_no,
                            "line": line,
                        })
                        continue

                    # Get user decision
                    entered_option = ""
                    opts = [f"    [{i + 1}] {word_suggestions[i]}" for i in range(len(word_suggestions))]
                    while not entered_option:
                        entered_option = click.prompt(
                            click.style(
                                f"  Please chose one of the following options:{os.linesep}" \
                                f"{os.linesep.join(opts)}{os.linesep}" \
                                f"    [-] Other:{os.linesep}" \
                                f"    [6] Add to Dictionary{os.linesep}" \
                                f"    [7] File Extension{os.linesep}" \
                                f"    [8] Code{os.linesep}" \
                                f"    [9] Skip{os.linesep}" \
                                f"    [0] Exit and Save{os.linesep}" \
                                f"   ", # [default]:
                                fg="magenta",
                            ),
                            default="1",
                        )

                    # Replace with selected suggestion
                    if entered_option in ["1", "2", "3", "4", "5"]:
                        fixed_word = word_suggestions[int(entered_option) - 1]
                    # Add to dictionary
                    elif entered_option == "6":
                        # TODO: update dictionary file and skip
                        fixed_word = ">ADD_TO_DICTIONARY<"
                    # File extension
                    elif entered_option == "7":
                        fixed_word = ">FILE_EXTENSION<"
                    # Code
                    elif entered_option == "8":
                        fixed_word = f"``{misspelled_word}``"
                    # Skip
                    elif entered_option == "9":
                        fixed_word = ">SKIP<"
                    # Exit and Save
                    elif entered_option == "0":
                        click.secho(f"Exiting...", fg="yellow")
                        return fixes
                    # Replace with user provided word
                    else:
                        fixed_word = entered_option

                    fixes[misspelled_word] = {
                        "files":[{
                            "filename": source_file,
                            "lineno": line_no,
                            "line": line,
                        }],
                        "misspelled_word": misspelled_word,
                        "fixed_word": fixed_word,
                        "suggestions": word_suggestions,
                    }

            except click.Abort:
                # Propagate Abort to kill the script on Keyboard interrupt
                raise
            except Exception as e:
                click.secho(f"ERROR: an unexpected error occurred while reading spelling output: {e}", fg="red")
                click.secho(f"       Skipping file...", fg="red")

    if errors:
        click.secho(f"Encountered {errors} errors out of {total} spelling mistakes.", fg="red")
    return fixes

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

                with curr_file.open('r') as f:
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
                        click.echo(
                            f"  {click.style('Changes saved!', fg="green")}"
                        )
                    else:
                        click.echo(
                            f"  {click.style('Dry Run:', bg="yellow")} Changes NOT saved."
                        )

                    files_updated.add(str(curr_file))
            except Exception as e:
                click.secho(f"ERROR: an unexpected error occurred while replacing links in {str(file)}: {e}", fg="red")
                click.secho(f"       Skipping file...", fg="red")

    click.secho(f"{os.linesep}Fixed {len(fixes)} links in {len(files_updated)} files.", fg="green")

def fix_spelling(links_type, links, docs_dir):
    fixes = dict()
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
                click.secho(f"ERROR: an unexpected error occurred while reading lines in {str(filename)}: {e}", fg="red")
                click.secho(f"       Skipping file...", fg="red")
                continue

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
                                progress_bar.update(1)
                                click.secho(os.linesep)
                                continue

                        click.secho(
                            "WARNING: Could not find link to replace in line:",
                            fg="yellow",
                        )
                        click.echo(f"         {link["lineno"]}: {lines[line_idx]}")
                        link["unfixed_reason"] = "Link not found in line."
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
                                click.secho(
                                    f"Exiting {links_type} links check...", fg="yellow"
                                )
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
                                if not 200 >= response.status_code < 300 and response.status_code not in [403, 406]:
                                    click.secho(
                                        f"  Error: URL returned status code {response.status_code}.",
                                        fg="red",
                                    )
                                    click.secho(
                                        "  Please enter a valid URL.", fg="red"
                                    )
                                    new_link = link["info"] if links_type == "redirected" else ""
                                    continue
                            except requests.RequestException as e:
                                click.secho(f"  Error: {e}", fg="red")
                                click.secho("  Please enter a valid URL.", fg="red")
                                new_link = link["info"] if links_type == "redirected" else ""
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
def check_spelling(dry_run):
    """Clean up the links in the documentation."""
    if dry_run:
        click.secho(
            f"Dry Run: No changes will be saved.",
            fg="yellow",
        )

    # Parse the linkcheck output
    docs_dir = Path(__file__).parents[1]
    project_root = docs_dir.parents[0]
    fixes = review_spell_check_output(docs_dir)
    click.echo(f"Found {len(fixes)} spelling mistakes to fix.")
    click.echo(f"Misspelled Words: {"\n".join(fixes.keys())}")

    # # Fix Redirected Links
    # redirect_fixes = fix_spelling("redirected", links["redirected"], docs_dir)
    # recursive_search_and_save(redirect_fixes, project_root, dry_run)

    # # Fix Broken Links
    # broken_fixes = fix_spelling("broken", links["broken"], docs_dir)
    # recursive_search_and_save(broken_fixes, project_root, dry_run)

    # Warning
    click.secho("WARNING: Please review the changes before committing.", fg="yellow")


if __name__ == "__main__":
    check_spelling()
