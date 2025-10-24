from tethys_cli.cli_colors import write_error, write_success, write_info
from tethys_cli.cli_helpers import setup_django
from tethys_portal.optional_dependencies import has_module


def add_cookie_parser(subparsers):
    if not has_module("cookie_consent"):
        return
    PURGE_COOKIES_COMMAND = "purge"
    LIST_COOKIES_COMMAND = "list"
    ADD_COOKIE_GROUP_COMMAND = "add_group"
    ADD_COOKIE_COMMAND = "add_cookie"
    DELETE_COOKIE_GROUP_COMMAND = "delete_group"
    DELETE_COOKIE_COMMAND = "delete_cookie"

    cookie_parser = subparsers.add_parser(
        "cookies", help="Cookie consent management commands for Tethys Platform."
    )
    cookie_parser.set_defaults(func=lambda args: cookie_parser.print_help())

    cookie_subparsers = cookie_parser.add_subparsers(
        title="Cookie Commands", dest="cookie-command"
    )

    # ########################################
    # ######### LIST COOKIES COMMAND #########
    # ########################################
    list_cookies_parser = cookie_subparsers.add_parser(
        LIST_COOKIES_COMMAND, help="List existing cookie groups and cookies."
    )

    list_cookies_parser.set_defaults(func=cli_list_cookies)

    # #########################################
    # ######### PURGE COOKIES COMMAND #########
    # #########################################
    purge_cookies_parser = cookie_subparsers.add_parser(
        PURGE_COOKIES_COMMAND, help="Purge existing cookie groups and cookies."
    )

    purge_cookies_parser.set_defaults(func=cli_purge_cookies)

    # ############################################
    # ######### ADD COOKIE GROUP COMMAND #########
    # ############################################
    add_cookie_group_parser = cookie_subparsers.add_parser(
        ADD_COOKIE_GROUP_COMMAND,
        help="Add a new cookie group (e.g. Necessary, Analytics, etc.).",
    )

    # ARGS
    add_cookie_group_parser.add_argument(
        "varname",
        help="Variable name for the cookie group (e.g. necessary, analytics, etc.).",
    )
    add_cookie_group_parser.add_argument(
        "name",
        help="Display name for the cookie group (e.g. Necessary, Analytics, etc.).",
    )
    add_cookie_group_parser.add_argument(
        "-d", "--description", help="Description of the cookie group.", default=""
    )
    add_cookie_group_parser.add_argument(
        "-r",
        "--is_required",
        action="store_true",
        help="Flag indicating if the cookie group is required. Default is False.",
        default=False,
    )
    add_cookie_group_parser.add_argument(
        "-x",
        "--is_deletable",
        action="store_true",
        help="Flag indicating if the cookie group is deletable. Default is True.",
        default=True,
    )
    add_cookie_group_parser.add_argument(
        "-o",
        "--ordering",
        type=int,
        help="Ordering of the cookie group. Default is the auto-incremented primary key.",
        default=0,
    )

    # CONFIGURE FUNCTION
    add_cookie_group_parser.set_defaults(func=cli_add_cookie_group)

    # #############################################
    # ########### ADD COOKIE COMMAND ##############
    # #############################################
    add_cookie_parser = cookie_subparsers.add_parser(
        ADD_COOKIE_COMMAND, help="Add a new cookie to an existing cookie group."
    )

    # ARGS
    add_cookie_parser.add_argument(
        "cookiegroup",
        help="Name of the cookie group to which the cookie belongs.",
    )
    add_cookie_parser.add_argument("name", help="Name of the cookie.")
    add_cookie_parser.add_argument(
        "-d",
        "--description",
        help="Description of the cookie.",
        default="",
    )
    add_cookie_parser.add_argument(
        "-p",
        "--path",
        help="Path of the cookie.",
        default="",
    )
    add_cookie_parser.add_argument(
        "-o",
        "--domain",
        help="Domain of the cookie.",
        default="",
    )

    # CONFIGURE FUNCTION
    add_cookie_parser.set_defaults(func=cli_add_cookie)

    # ############################################
    # ####### DELETE COOKIE GROUP COMMAND ########
    # ############################################
    delete_cookie_group_parser = cookie_subparsers.add_parser(
        DELETE_COOKIE_GROUP_COMMAND,
        help="Delete cookie group (e.g. Necessary, Analytics, etc.).",
    )
    delete_cookie_group_parser.add_argument(
        "varname", help="Variable name of the cookie group to delete."
    )
    delete_cookie_group_parser.add_argument(
        "-c",
        "--cascade",
        action="store_true",
        help="Delete all cookies associated with the group. If False, the cookie group must be empty. Default is False.",
        default=False,
    )

    delete_cookie_group_parser.set_defaults(func=cli_delete_cookie_group)

    # ###################### ###############
    # ####### DELETE COOKIE COMMAND ########
    # ######################################
    delete_cookie_group_parser = cookie_subparsers.add_parser(
        DELETE_COOKIE_COMMAND, help="Delete cookie from an existing cookie group."
    )
    delete_cookie_group_parser.add_argument(
        "group", help="Variable name of the cookie group to which the cookie belongs."
    )
    delete_cookie_group_parser.add_argument(
        "name", help="Name of the cookie to delete."
    )

    delete_cookie_group_parser.set_defaults(func=cli_delete_cookie)


def cli_add_cookie_group(args):
    setup_django()
    from cookie_consent.models import CookieGroup

    try:
        CookieGroup.objects.create(
            varname=args.varname,
            name=args.name,
            description=args.description,
            is_required=args.is_required,
            is_deletable=args.is_deletable,
            ordering=args.ordering,
        )
        write_success(f"Cookie group '{args.name}' added.")
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            write_error(f"Cookie group '{args.varname}' already exists.")
            exit(1)


def cli_add_cookie(args):
    setup_django()
    from cookie_consent.models import Cookie, CookieGroup

    try:
        Cookie.objects.create(
            cookiegroup=CookieGroup.objects.get(varname=args.cookiegroup),
            name=args.name,
            description=args.description,
            path=args.path,
            domain=args.domain,
        )
        write_success(f"Cookie '{args.name}' added.")
    except Exception as e:
        if "does not exist" in str(e):
            write_error(f"Cookie group '{args.cookiegroup}' does not exist.")
            exit(1)


def cli_delete_cookie_group(args):
    setup_django()
    from cookie_consent.models import CookieGroup, Cookie

    try:
        group_has_cookies = Cookie.objects.filter(
            cookiegroup__varname=args.varname
        ).exists()
        if group_has_cookies and not args.cascade:
            raise Exception(
                f"Cookie group '{args.varname}' has associated cookies. Use cascade=True to delete it and its cookies."
            )
        CookieGroup.objects.get(varname=args.varname).delete()
        write_success(f"Cookie group '{args.varname}' deleted.")
    except Exception as e:
        if "does not exist" in str(e):
            write_error(f"Cookie group '{args.varname}' does not exist.")
        elif "associated cookies" in str(e):
            write_error(str(e))
            exit(1)


def cli_delete_cookie(args):
    setup_django()
    from cookie_consent.models import Cookie, CookieGroup

    try:
        cookie_group = CookieGroup.objects.get(varname=args.group)
        Cookie.objects.get(cookiegroup=cookie_group, name=args.name).delete()
        write_success(f"Cookie '{args.name}' deleted from group '{args.group}'.")
    except Exception as e:
        if "CookieGroup matching query does not exist" in str(e):
            write_error(f"Cookie group '{args.group}' does not exist.")
            exit(1)
        elif "Cookie matching query does not exist" in str(e):
            write_error(f"Cookie '{args.name}' does not exist in group '{args.group}'.")
            exit(1)


def cli_list_cookies(_):
    setup_django()
    from cookie_consent.models import CookieGroup

    groups = CookieGroup.objects.all().order_by("varname")
    for group in groups:
        write_info(f"{group.name} ({group.varname}):")
        write_info(f"  Description: {group.description}")
        write_info(f"  Required: {'Yes' if group.is_required else 'No'}")
        write_info(f"  Deletable: {'Yes' if group.is_deletable else 'No'}")
        write_info(f"  Ordering: {group.ordering}")
        write_info(f"  Created At: {group.created}")
        write_info("  Cookies:")
        cookies = group.cookie_set.all()
        if cookies:
            for cookie in cookies:
                write_info(f"   -  Name: {cookie.name}")
                write_info(f"      Description: {cookie.description}")
                write_info(f"      Path: {cookie.path}")
                write_info(f"      Domain: {cookie.domain}")
        else:
            write_info("  - No cookies in this group.")


def cli_purge_cookies(_):
    setup_django()
    from cookie_consent.models import Cookie, CookieGroup

    Cookie.objects.all().delete()
    CookieGroup.objects.all().delete()
    write_success("All cookie groups and cookies have been deleted.")
