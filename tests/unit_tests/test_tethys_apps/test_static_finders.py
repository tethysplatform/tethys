from pathlib import Path
import pytest
from tethys_apps.static_finders import TethysStaticFinder


@pytest.fixture
def static_finder_root():
    src_dir = Path(__file__).parents[3]
    root = (
        src_dir
        / "tests"
        / "apps"
        / "tethysapp-test_app"
        / "tethysapp"
        / "test_app"
        / "public"
    )
    return {"src_dir": src_dir, "root": root}


@pytest.mark.django_db
def test_find(test_app):
    tethys_static_finder = TethysStaticFinder()
    path = Path("test_app") / "css" / "main.css"
    expected_path = Path("test_app") / "public" / "css" / "main.css"
    path_ret = tethys_static_finder.find(path)
    assert str(expected_path) in str(path_ret)
    str_ret = tethys_static_finder.find(str(path))
    assert str(expected_path) in str(str_ret)


@pytest.mark.django_db
def test_find_all(test_app):
    import django

    tethys_static_finder = TethysStaticFinder()
    path = Path("test_app") / "css" / "main.css"
    use_find_all = django.VERSION >= (5, 2)
    if use_find_all:
        path_ret = tethys_static_finder.find(path, find_all=True)
        str_ret = tethys_static_finder.find(str(path), find_all=True)
    else:
        path_ret = tethys_static_finder.find(path, all=True)
        str_ret = tethys_static_finder.find(str(path), all=True)
    expected_path = Path("test_app") / "public" / "css" / "main.css"
    path_ret = tethys_static_finder.find(path)
    assert str(expected_path) in str(path_ret)
    str_ret = tethys_static_finder.find(str(path))
    assert str(expected_path) in str(str_ret)


def test_find_location_with_no_prefix(static_finder_root):
    prefix = None
    path = Path("css") / "main.css"
    root = static_finder_root["root"]
    tethys_static_finder = TethysStaticFinder()
    path_ret = tethys_static_finder.find_location(root, path, prefix)
    assert root / path == path_ret
    str_ret = tethys_static_finder.find_location(str(root), path, prefix)
    assert root / path == str_ret


def test_find_location_with_prefix_not_in_path(static_finder_root):
    prefix = "tethys_app"
    path = Path("css") / "main.css"
    root = static_finder_root["root"]
    tethys_static_finder = TethysStaticFinder()
    path_ret = tethys_static_finder.find_location(root, path, prefix)
    assert path_ret is None
    str_ret = tethys_static_finder.find_location(str(root), path, prefix)
    assert str_ret is None


def test_find_location_with_prefix_in_path(static_finder_root):
    prefix = "tethys_app"
    path = Path("tethys_app") / "css" / "main.css"
    root = static_finder_root["root"]
    tethys_static_finder = TethysStaticFinder()
    path_ret = tethys_static_finder.find_location(root, path, prefix)
    assert root / "css" / "main.css" == path_ret
    str_ret = tethys_static_finder.find_location(str(root), path, prefix)
    assert root / "css" / "main.css" == str_ret


@pytest.mark.django_db
def test_list(test_app):
    tethys_static_finder = TethysStaticFinder()
    expected_ignore_patterns = ""
    expected_app_paths = []
    for path, storage in tethys_static_finder.list(expected_ignore_patterns):
        if "test_app" in storage.location:
            expected_app_paths.append(path)
    assert str(Path("js") / "main.js") in expected_app_paths
    assert str(Path("images") / "icon.gif") in expected_app_paths
    assert str(Path("css") / "main.css") in expected_app_paths
