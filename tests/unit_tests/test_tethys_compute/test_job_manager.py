import pytest
from unittest import mock
from django.contrib.auth.models import User, Group
from tethys_compute.job_manager import JobManager, JOB_TYPES
from tethys_compute.models.tethys_job import TethysJob
from tethys_compute.models.condor.condor_scheduler import CondorScheduler
from tethys_apps.models import TethysApp


# Module-scoped fixture for setup/teardown
@pytest.fixture(scope="function")
def setup_job_manager():
    app_model = TethysApp(name="test_app_job_manager", package="test_app_job_manager")
    app_model.save()

    user_model = User.objects.create_user(
        username="test_user_job_manager", email="user@example.com", password="pass"
    )

    group_model = Group.objects.create(name="test_group_job_manager")
    group_model.user_set.add(user_model)

    scheduler = CondorScheduler(
        name="test_scheduler",
        host="localhost",
    )
    scheduler.save()

    tethysjob = TethysJob(
        name="test_tethysjob",
        description="test_description",
        user=user_model,
        label="test_app_job_manager",
    )
    tethysjob.save()
    tethysjob.groups.add(group_model)

    yield {
        "app_model": app_model,
        "user_model": user_model,
        "group_model": group_model,
        "scheduler": scheduler,
        "tethysjob": tethysjob,
    }

    tethysjob.delete()
    scheduler.delete()
    group_model.delete()
    user_model.delete()
    app_model.delete()


@pytest.mark.django_db
def test_JobManager_init():
    mock_app = mock.MagicMock()
    mock_app.package = "test_label"
    ret = JobManager(mock_app)
    assert mock_app == ret.app
    assert ret.label == "test_label"


@pytest.mark.django_db
@mock.patch("tethys_compute.job_manager.get_user_workspace")
def test_JobManager_create_job_custom_class(mock_guw, setup_job_manager):
    mock_guw().path = "test_user_workspace"
    app_model = setup_job_manager["app_model"]
    user_model = setup_job_manager["user_model"]
    group_model = setup_job_manager["group_model"]
    ret_jm = JobManager(app_model)
    ret_job = ret_jm.create_job(
        name="test_create_tethys_job",
        user=user_model,
        job_type=TethysJob,
        groups=group_model,
    )
    assert ret_job.name == "test_create_tethys_job"
    assert ret_job.user == user_model
    assert ret_job.label == "test_app_job_manager"
    assert group_model in ret_job.groups.all()
    ret_job.delete()


@pytest.mark.django_db
@mock.patch("tethys_compute.job_manager.get_user_workspace")
@mock.patch("tethys_compute.job_manager.CondorJob")
def test_JobManager_create_job_string(mock_cj, mock_guw):
    mock_app = mock.MagicMock()
    mock_app.package = "test_label"
    mock_guw().path = "test_user_workspace"
    ret_jm = JobManager(mock_app)
    with mock.patch.dict(JOB_TYPES, {"CONDOR": mock_cj}):
        ret_jm.create_job(name="test_name", user="test_user", job_type="CONDOR")
    mock_cj.assert_called_with(
        label="test_label",
        name="test_name",
        user="test_user",
        workspace="test_user_workspace",
    )


@pytest.mark.django_db
@mock.patch("tethys_compute.job_manager.isinstance")
@mock.patch("tethys_compute.job_manager.get_anonymous_user")
@mock.patch("tethys_compute.job_manager.get_user_workspace")
@mock.patch("tethys_compute.job_manager.CondorJob")
def test_JobManager_create_job_anonymous_user(
    mock_cj, mock_guw, mock_get_anonymous_user, mock_isinstance
):
    mock_app = mock.MagicMock()
    mock_app.package = "test_label"
    mock_guw().path = "test_user_workspace"
    mock_user = mock.MagicMock(is_staff=False, is_anonymous=True)
    mock_user.has_perm.return_value = False
    mock_anonymous_user = mock.MagicMock(is_staff=False)
    mock_anonymous_user.has_perm.return_value = False
    mock_get_anonymous_user.return_value = mock_anonymous_user
    mock_isinstance.return_value = True
    ret_jm = JobManager(mock_app)
    with mock.patch.dict(JOB_TYPES, {"CONDOR": mock_cj}):
        ret_jm.create_job(name="test_name", user=mock_user, job_type="CONDOR")
    mock_cj.assert_called_with(
        label="test_label",
        name="test_name",
        user=mock_anonymous_user,
        workspace="test_user_workspace",
    )


@pytest.mark.django_db
def test_JobManager_list_job_with_user(setup_job_manager):
    app_model = setup_job_manager["app_model"]
    user_model = setup_job_manager["user_model"]
    tethysjob = setup_job_manager["tethysjob"]
    mgr = JobManager(app_model)
    ret = mgr.list_jobs(user=user_model)
    assert ret[0] == tethysjob


@pytest.mark.django_db
def test_JobManager_list_job_with_groups(setup_job_manager):
    app_model = setup_job_manager["app_model"]
    group_model = setup_job_manager["group_model"]
    tethysjob = setup_job_manager["tethysjob"]
    mgr = JobManager(app_model)
    ret = mgr.list_jobs(groups=[group_model])
    assert ret[0] == tethysjob


@pytest.mark.django_db
def test_JobManager_list_job_value_error(setup_job_manager):
    app_model = setup_job_manager["app_model"]
    user_model = setup_job_manager["user_model"]
    group_model = setup_job_manager["group_model"]
    mgr = JobManager(app_model)
    with pytest.raises(ValueError):
        mgr.list_jobs(user=user_model, groups=[group_model])


@pytest.mark.django_db
@mock.patch("tethys_compute.job_manager.TethysJob")
def test_JobManager_get_job(mock_tethys_job):
    mock_args = mock.MagicMock()
    mock_app_package = mock.MagicMock()
    mock_args.package = mock_app_package
    mock_jobs = mock.MagicMock()
    mock_tethys_job.objects.get_subclass.return_value = mock_jobs
    mock_job_id = "fooid"
    mock_user = "bar"
    mgr = JobManager(mock_args)
    ret = mgr.get_job(job_id=mock_job_id, user=mock_user)
    assert ret == mock_jobs
    mock_tethys_job.objects.get_subclass.assert_called_once_with(
        id="fooid", label=mock_app_package, user="bar"
    )


@pytest.mark.django_db
@mock.patch("tethys_compute.job_manager.TethysJob")
def test_JobManager_get_job_dne(mock_tethys_job):
    mock_args = mock.MagicMock()
    mock_app_package = mock.MagicMock()
    mock_args.package = mock_app_package
    mock_tethys_job.DoesNotExist = TethysJob.DoesNotExist
    mock_tethys_job.objects.get_subclass.side_effect = TethysJob.DoesNotExist
    mock_job_id = "fooid"
    mock_user = "bar"
    mgr = JobManager(mock_args)
    ret = mgr.get_job(job_id=mock_job_id, user=mock_user)
    assert ret is None
    mock_tethys_job.objects.get_subclass.assert_called_once_with(
        id="fooid", label=mock_app_package, user="bar"
    )


@pytest.mark.django_db
def test_JobManager_get_job_status_callback_url():
    mock_args = mock.MagicMock()
    mock_request = mock.MagicMock()
    mock_job_id = "foo"
    mgr = JobManager(mock_args)
    mgr.get_job_status_callback_url(mock_request, mock_job_id)
    mock_request.build_absolute_uri.assert_called_once_with("/update-job-status/foo/")
