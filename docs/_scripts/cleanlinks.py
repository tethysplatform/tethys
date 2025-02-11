import json
from pathlib import Path
import os
import sys

import click


def group_by_file(links):
    files = {}
    for link in links:
        if link["filename"] not in files:
            files[link["filename"]] = []
        files[link["filename"]].append(link)
    return files


@click.command()
@click.option("-dry", "--dry-run", "dry_run", is_flag=True, help="Do not make any changes.")
def clean_links(dry_run):
    """Clean up the links in the documentation."""
    docs_dir = Path(__file__).parents[1]
    build_dir = docs_dir / "_build"
    linkcheck_dir = build_dir / "linkcheck"
    linkcheck_out = linkcheck_dir / "output.json"

    click.echo("Searching for linkcheck output...")
    if not build_dir.exists() or not linkcheck_dir.exists() or not linkcheck_out.exists():
        click.echo("Could not find linkcheck output (output.json).")
        click.echo('Please, run "make linkcheck" first and try again.')
        sys.exit(1)

    click.echo(f"Using linkcheck output at {linkcheck_out}")
    click.echo("Reading linkcheck output...")

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

    # Fix the Redirected Links
    fix_redirected = click.prompt(click.style(f"{os.linesep}Would you like to {len(links['redirected'])} fix redirected links? [y/n]", fg="magenta"), default="y")
    redirect_not_fixed = links["redirected"]

    if fix_redirected.lower() == "y":
        review_each = click.prompt(click.style(f"Would you like to review each redirect fix [r] or fix automatically [a]?", fg="magenta"), default="r")
        review_each = review_each.lower() == "r"
        click.echo("Fixing redirected links...")
        redirect_files = group_by_file(links["redirected"])
        redirect_not_fixed = []
        for filename, redirect_links in redirect_files.items():
            click.secho(f"{os.linesep}{filename}", fg="blue")
            with open(docs_dir / filename, "r") as f:
                lines = f.readlines()

            # Replace each link in the file
            for link in redirect_links:
                original_link = link["uri"]
                new_link = link["info"]
                click.echo(f"{os.linesep}  {click.style(link['lineno'], bold=True)}: {click.style(original_link, bg="magenta")} -> {click.style(new_link, bg="magenta")}")

                try:
                    line_idx = link["lineno"] - 1
                    line = lines[line_idx].strip()

                    # Check if the link is in the line
                    found = line.find(original_link)
                    if not found:
                        click.secho(f"WARNING: Could not find link to replace in line:", fg="yellow")
                        click.echo(f"         {link["lineno"]}: {lines[line_idx]}")
                        redirect_not_fixed.append(link)
                        continue

                    # Replace the link
                    if review_each:
                        click.echo(f'  {click.style('Line', bold=True)}: {line}')
                        click.echo(f'  {click.style('Code', bold=True)}: {link["code"]}')
                        new_link = click.prompt(click.style("  Please enter new URL or press Enter to skip", fg="magenta"), default=new_link)
                        if not new_link:
                            click.secho("  Skipped", fg="yellow")
                            redirect_not_fixed.append(link)

                    click.secho(f"  Replacing: {original_link} -> {new_link}", fg="green")
                    lines[line_idx] = lines[line_idx].replace(original_link, new_link)
                except click.Abort:
                    # Propagate Abort to kill the script on Keyboard interrupt
                    raise
                except IndexError:
                    click.secho("ERROR: Could not find line.", fg="red")
                    continue
                except Exception as e:
                    click.echo(type(e))
                    click.secho(f"ERROR: {e}", fg="red")

            if not dry_run:
                with open(docs_dir / filename, "w") as f:
                    f.writelines(lines)

    # Broken Links
    fix_broken = click.prompt(click.style(f"{os.linesep}Would you like to {len(links['broken'])} fix broken links? [y/n]", fg="magenta"), default="y")
    skipped_broken_links = links["broken"]
    if fix_broken.lower() == "y":
        click.secho(f"{os.linesep}Fixing broken links...", bg="magenta")
        broken_files = group_by_file(links["broken"])
        skipped_broken_links = []
        for filename, broken_links in broken_files.items():
            click.secho(f"{os.linesep}{filename}", fg="blue")
            with open(docs_dir / filename, "r") as f:
                lines = f.readlines()

            for link in broken_links:
                original_link = link["uri"]
                try:
                    line_idx = link["lineno"] - 1
                    line = lines[line_idx].strip()

                    # Check if the link is in the line
                    found = line.find(original_link)
                    if not found:
                        click.secho(f"WARNING: Could not find broken link in line:", fg="yellow")
                        click.echo(f"         {link['uri']} -> {link['lineno']}: {line}")
                        skipped_broken_links.append(link)
                        continue

                    click.echo(f"{os.linesep}  {click.style(link['lineno'], bold=True)}: {click.style(link['uri'], bg="magenta")}")
                    click.echo(f'  {click.style('Line', bold=True)}: {line}')
                    click.echo(f'  {click.style('Info', bold=True)}: {link["info"]}')

                    new_url = click.prompt(click.style("  Please enter new URL or press Enter to skip", fg="magenta"), default="")
                    if not new_url:
                        click.secho("  Skipped", fg="yellow")
                        skipped_broken_links.append(link)
                        continue

                    click.secho(f"  Replacing: {link['uri']} -> {new_url}", fg="green")
                    lines[line_idx] = lines[line_idx].replace(original_link, new_url)
                except click.Abort:
                    # Propagate Abort to kill the script on Keyboard interrupt
                    raise
                except IndexError:
                    click.secho("ERROR: Could not find line.", fg="red")
                    continue

        if not dry_run:
            with open(docs_dir / filename, "w") as f:
                f.writelines(lines)


    # Summary Report
    click.secho("Link Check Summary:", fg="blue")
    click.echo(f"  Working: {len(links['working'])}")
    click.echo(f"  Ignored: {len(links['ignored'])}")
    broken_fixed = len(links["broken"]) - len(skipped_broken_links)
    click.echo(f"  Broken: {broken_fixed}/{len(links['broken'])}")
    click.echo(f"  Timeout: {len(links['timeout'])}")
    redirect_fixed = len(links["redirected"]) - len(redirect_not_fixed)
    click.echo(f"  Redirected: {redirect_fixed}/{len(links['redirected'])}")
    click.echo(f"  Other: {len(links['other'])}")
    click.echo(f"  Total: {len(lines)}")
    click.echo(f"  Files: {len(files)}")



if __name__ == "__main__":
    clean_links()