import pytest
from pathlib import Path
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
    return root


@pytest.mark.django_db
def test_find():
    tethys_static_finder = TethysStaticFinder()
    path = Path("test_app") / "css" / "main.css"
    expected_path = str(Path("test_app/public/css/main.css"))
    path_ret = tethys_static_finder.find(path)
    assert isinstance(path_ret, Path)
    assert expected_path in str(path_ret)
    str_ret = tethys_static_finder.find(str(path))
    assert isinstance(str_ret, Path)
    assert expected_path in str(str_ret)


@pytest.mark.django_db
def test_find_all():
    import django

    tethys_static_finder = TethysStaticFinder()
    path = Path("test_app") / "css" / "main.css"
    expected_path = str(Path("test_app/public/css/main.css"))
    use_find_all = django.VERSION >= (5, 2)
    if use_find_all:
        path_ret = tethys_static_finder.find(path, find_all=True)
        str_ret = tethys_static_finder.find(str(path), find_all=True)
    else:
        path_ret = tethys_static_finder.find(path, all=True)
        str_ret = tethys_static_finder.find(str(path), all=True)
    assert len(path_ret) == 1
    assert isinstance(path_ret[0], Path)
    assert len(str_ret) == 1
    assert isinstance(str_ret[0], Path)
    assert expected_path in str(path_ret[0])
    assert expected_path in str(str_ret[0])


def test_find_location_with_no_prefix(static_finder_root):
    prefix = None
    path = Path("css") / "main.css"

    tethys_static_finder = TethysStaticFinder()
    path_ret = tethys_static_finder.find_location(static_finder_root, path, prefix)
    assert static_finder_root / path == path_ret
    str_ret = tethys_static_finder.find_location(str(static_finder_root), path, prefix)
    assert static_finder_root / path == str_ret


def test_find_location_with_prefix_not_in_path(static_finder_root):
    prefix = "tethys_app"
    path = Path("css") / "main.css"

    tethys_static_finder = TethysStaticFinder()
    path_ret = tethys_static_finder.find_location(static_finder_root, path, prefix)
    assert path_ret is None
    str_ret = tethys_static_finder.find_location(str(static_finder_root), path, prefix)
    assert str_ret is None


def test_find_location_with_prefix_in_path(static_finder_root):
    prefix = "tethys_app"
    path = Path("tethys_app") / "css" / "main.css"

    tethys_static_finder = TethysStaticFinder()
    path_ret = tethys_static_finder.find_location(static_finder_root, path, prefix)
    assert static_finder_root / "css" / "main.css" == path_ret
    str_ret = tethys_static_finder.find_location(str(static_finder_root), path, prefix)
    assert static_finder_root / "css" / "main.css" == str_ret


@pytest.mark.django_db
def test_list(static_finder_root):
    tethys_static_finder = TethysStaticFinder()
    expected_ignore_patterns = ""
    expected_app_paths = []
    for path, storage in tethys_static_finder.list(expected_ignore_patterns):
        if "test_app" in storage.location:
            expected_app_paths.append(path)

    assert str(Path("js") / "main.js") in expected_app_paths
    assert str(Path("images") / "icon.gif") in expected_app_paths
    assert str(Path("css") / "main.css") in expected_app_paths
