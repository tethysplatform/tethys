import unittest
import mock
import tethys_apps.cli.docker_commands as cli_docker_commands


class TestDockerCommands(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_max_to_prompt(self):
        self.assertEquals(' (max Foo)', cli_docker_commands.add_max_to_prompt('', 'Foo'))

    def test_add_default_to_prompt(self):
        self.assertEquals(' [Foo]', cli_docker_commands.add_default_to_prompt('', 'Foo'))

    def test_add_default_to_prompt_with_choice(self):
        self.assertEquals(' [Foo/bar]', cli_docker_commands.add_default_to_prompt('', 'Foo', choices=['Foo', 'Bar']))

    def test_close_prompt(self):
        self.assertEquals('Bar: ', cli_docker_commands.close_prompt('Bar'))

    def test_validate_numeric_cli_input_with_no_value(self):
        self.assertEquals('12', cli_docker_commands.validate_numeric_cli_input('', default=12, max=100))

    def test_validate_numeric_cli_input_with_value(self):
        self.assertEquals(50, cli_docker_commands.validate_numeric_cli_input(50, default=12, max=100))

    @mock.patch('tethys_apps.cli.docker_commands.input')
    def test_validate_numeric_cli_input_with_value_gt_max(self, mock_input):
        mock_input.side_effect = [55]
        self.assertEquals(55, cli_docker_commands.validate_numeric_cli_input(200, default=12, max=100))

    @mock.patch('tethys_apps.cli.docker_commands.input')
    def test_validate_numeric_cli_input_with_value_gt_max_no_default(self, mock_input):
        mock_input.side_effect = [66]
        self.assertEquals(66, cli_docker_commands.validate_numeric_cli_input(200, max=100))

    @mock.patch('tethys_apps.cli.docker_commands.input')
    def test_validate_numeric_cli_input_value_error(self, mock_input):
        mock_input.side_effect = [23]
        self.assertEquals(23, cli_docker_commands.validate_numeric_cli_input(value='123ABC', default=12, max=100))

    def test_validate_choice_cli_input_no_value(self):
        self.assertEquals('Bar', cli_docker_commands.validate_choice_cli_input('', '', default='Bar'))

    @mock.patch('tethys_apps.cli.docker_commands.input')
    def test_validate_choice_cli_input(self, mock_input):
        mock_input.side_effect = ['Foo']
        self.assertEquals('Foo', cli_docker_commands.validate_choice_cli_input('Bell', choices=['foo', 'bar'],
                                                                               default='bar'))

    def test_validate_directory_cli_input_no_value(self):
        self.assertEquals('/tmp', cli_docker_commands.validate_directory_cli_input('', default='/tmp'))

    @mock.patch('tethys_apps.cli.docker_commands.os.path.isdir')
    def test_validate_directory_cli_input_is_dir(self, mock_os_path_isdir):
        mock_os_path_isdir.return_value = True
        self.assertEquals('/c://temp//foo//bar', cli_docker_commands.validate_directory_cli_input('c://temp//foo//bar',
                                                                                                  default='c://temp//'))

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.input')
    @mock.patch('tethys_apps.cli.docker_commands.os.makedirs')
    @mock.patch('tethys_apps.cli.docker_commands.os.path.isdir')
    def test_validate_directory_cli_input_oserror(self, mock_os_path_isdir, mock_os_makedirs, mock_input,
                                                  mock_pretty_output):
        mock_os_path_isdir.side_effect = [False, True]
        mock_os_makedirs.side_effect = OSError
        mock_input.side_effect = ['/foo/tmp']
        self.assertEquals('/foo/tmp', cli_docker_commands.validate_directory_cli_input('c://temp//foo//bar',
                                                                                       default='c://temp//'))
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('OSError(): /c://temp//foo//bar', po_call_args[0][0][0])

    def test_get_api_version(self):
        versions = ('1.2', '1.3')
        self.assertEquals(versions, cli_docker_commands.get_api_version(versions))

    @mock.patch('tethys_apps.cli.docker_commands.get_api_version')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_get_docker_client_linux(self, mock_DockerClient, mock_get_api_version):
        ret = cli_docker_commands.get_docker_client()
        mock_get_api_version.assert_called()
        call_args = mock_DockerClient.call_args_list

        self.assertEqual(2, len(call_args))
        # Validate first call
        first_call = call_args[0]
        self.assertEqual('unix://var/run/docker.sock', first_call[1]['base_url'])
        self.assertEqual('1.12', first_call[1]['version'])

        # Validate second call
        second_call = call_args[1]
        self.assertEqual('unix://var/run/docker.sock', second_call[1]['base_url'])
        self.assertEqual(mock_get_api_version(), second_call[1]['version'])

        # Validate result
        self.assertEqual(mock_DockerClient(), ret)

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_api_version')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    @mock.patch('tethys_apps.cli.docker_commands.kwargs_from_env')
    @mock.patch('tethys_apps.cli.docker_commands.os.environ')
    @mock.patch('tethys_apps.cli.docker_commands.json.loads')
    @mock.patch('tethys_apps.cli.docker_commands.subprocess')
    def test_get_docker_client_mac_no_os_environ(self, mock_subprocess, mock_json_loads, mock_os_environ,
                                                 mock_kwargs, mock_docker_client, mock_get_api_version,
                                                 mock_pretty_output):
        mock_p = mock.MagicMock()
        mock_p.communicate.return_value = ['DOCKER_HOST=bar_host:9 DOCKER_CERT_PATH=baz_path DOCKER_TLS_VERIFY=qux_tls']
        mock_subprocess.Popen.return_value = mock_p
        mock_json_loads.return_value = {"State": "foo", "DOCKER_HOST": "bar", "DOCKER_CERT_PATH": "baz",
                                        "DOCKER_TLS_VERIFY": "qux"}
        mock_os_environ.return_value = {}
        mock_kwargs.return_value = {}
        mock_version_client = mock.MagicMock()
        mock_version_client.version.return_value = {'ApiVersion': 'quux'}
        mock_docker_client.return_value = mock_version_client
        mock_get_api_version.return_value = 'corge'

        ret = cli_docker_commands.get_docker_client()

        self.assertEquals('9', ret.host)
        self.assertEquals(mock_docker_client(), ret)
        mock_subprocess.Popen.assert_any_call(['boot2docker', 'info'], stdout=-1)
        mock_subprocess.call.assert_called_once_with(['boot2docker', 'start'])
        mock_subprocess.Popen.assert_called_with(['boot2docker', 'shellinit'], stdout=-1)
        mock_json_loads.asssert_called_once()
        mock_os_environ.__setitem__.assert_any_call('DOCKER_TLS_VERIFY', 'qux_tls')
        mock_os_environ.__setitem__.assert_any_call('DOCKER_HOST', 'bar_host:9')
        mock_os_environ.__setitem__.assert_any_call('DOCKER_CERT_PATH', 'baz_path')
        mock_kwargs.assert_called_once_with(assert_hostname=False)
        mock_docker_client.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('Starting Boot2Docker VM:', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_api_version')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    @mock.patch('tethys_apps.cli.docker_commands.kwargs_from_env')
    @mock.patch('tethys_apps.cli.docker_commands.json.loads')
    @mock.patch('tethys_apps.cli.docker_commands.subprocess')
    def test_get_docker_client_mac_docker_host_env(self, mock_subprocess, mock_json_loads, mock_kwargs,
                                                   mock_docker_client, mock_get_api_version,
                                                   mock_pretty_output):
        mock_p = mock.MagicMock()
        mock_p.communicate.return_value = ['DOCKER_HOST=bar_host:5555 DOCKER_CERT_PATH=baz_path '
                                           'DOCKER_TLS_VERIFY=qux_tls']
        mock_subprocess.Popen.return_value = mock_p
        mock_json_loads.return_value = {"State": "foo", "DOCKER_HOST": "bar", "DOCKER_CERT_PATH": "baz",
                                        "DOCKER_TLS_VERIFY": "qux"}
        mock_kwargs.return_value = {}
        mock_version_client = mock.MagicMock()
        mock_version_client.version.return_value = {'ApiVersion': 'quux'}
        mock_docker_client.return_value = mock_version_client
        mock_get_api_version.return_value = 'corge'

        with mock.patch.dict('tethys_apps.cli.docker_commands.os.environ', {'DOCKER_HOST': 'foo=888:777',
                                                                            'DOCKER_CERT_PATH': 'bar',
                                                                            'DOCKER_TLS_VERIFY': 'baz'}, clear=True):
            ret = cli_docker_commands.get_docker_client()

        self.assertEquals('777', ret.host)
        self.assertEquals(mock_docker_client(), ret)
        mock_subprocess.Popen.assert_called_once_with(['boot2docker', 'info'], stdout=-1)
        mock_subprocess.call.assert_called_once_with(['boot2docker', 'start'])
        mock_json_loads.asssert_called_once()
        mock_kwargs.assert_called_once_with(assert_hostname=False)
        mock_docker_client.assert_called()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('Starting Boot2Docker VM:', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.subprocess.Popen')
    def test_get_docker_client_other(self, mock_subprocess):
        mock_subprocess.side_effect = Exception
        self.assertRaises(Exception, cli_docker_commands.get_docker_client)

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.subprocess')
    def test_stop_boot2docker(self, mock_subprocess, mock_pretty_output):
        cli_docker_commands.stop_boot2docker()
        mock_subprocess.call.assert_called_with(['boot2docker', 'stop'])
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('Boot2Docker VM Stopped', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.subprocess.call')
    def test_stop_boot2docker_os_error(self, mock_subprocess):
        mock_subprocess.side_effect = OSError
        cli_docker_commands.stop_boot2docker()
        mock_subprocess.assert_called_once_with(['boot2docker', 'stop'])

    @mock.patch('tethys_apps.cli.docker_commands.subprocess.call')
    def test_stop_boot2docker_exception(self, mock_subprocess):
        mock_subprocess.side_effect = Exception
        self.assertRaises(Exception, cli_docker_commands.stop_boot2docker)

    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_get_images_to_install(self, mock_dc):
        mock_dc.images.return_value = [{'RepoTags': 'ciwater/postgis:2.1.2'},
                                       {'RepoTags': 'ciwater/geoserver:2.8.2-clustered'}]

        # mock docker client return images
        all_docker_input = ('postgis', 'geoserver', 'wps')
        ret = cli_docker_commands.get_images_to_install(mock_dc, all_docker_input)

        self.assertEquals(1, len(ret))
        self.assertEquals('ciwater/n52wps:3.3.1', ret[0])

    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_get_containers_to_create(self, mock_dc):
        # mock_dc.containers.return_value = [{'Names': '/tethys_postgis'},
        #                                    {'Names': '/tethys_geoserver'}]
        mock_dc.containers.return_value = [{'Names': ['/tethys_postgis'], 'Image': '/tethys_postgis'},
                                           {'Names': ['/tethys_geoserver'], 'Image': '/tethys_geoserver'}]
        all_container_input = ('postgis', 'geoserver', 'wps')
        ret = cli_docker_commands.get_containers_to_create(mock_dc, all_container_input)

        self.assertEquals(1, len(ret))
        self.assertEquals('tethys_wps', ret[0])

    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_get_docker_container_dicts(self, mock_dc):
        mock_dc.containers.return_value = [{'Names': ['/tethys_postgis'], 'Image': '/tethys_postgis'},
                                           {'Names': ['/tethys_geoserver'], 'Image': '/tethys_geoserver'},
                                           {'Names': ['/tethys_wps'], 'Image': '/tethys_wps'}]
        ret = cli_docker_commands.get_docker_container_dicts(mock_dc)

        self.assertEquals(3, len(ret))
        self.assertTrue('tethys_postgis' in ret)
        self.assertTrue('tethys_geoserver' in ret)
        self.assertTrue('tethys_wps' in ret)

    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_get_docker_container_image(self, mock_dc):
        mock_dc.containers.return_value = [{'Names': ['/tethys_postgis'], 'Image': '/tethys_postgis'},
                                           {'Names': ['/tethys_geoserver'], 'Image': '/tethys_geoserver'},
                                           {'Names': ['/tethys_wps'], 'Image': '/tethys_wps'}]
        ret = cli_docker_commands.get_docker_container_image(mock_dc)

        self.assertEquals(3, len(ret))
        self.assertTrue('tethys_postgis' in ret)
        self.assertTrue('tethys_geoserver' in ret)
        self.assertTrue('tethys_wps' in ret)

    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_get_docker_container_status(self, mock_dc):
        mock_dc.containers.return_value = [{'Names': ['/tethys_postgis'], 'Image': '/tethys_postgis'},
                                           {'Names': ['/tethys_geoserver'], 'Image': '/tethys_geoserver'},
                                           {'Names': ['/tethys_wps'], 'Image': '/tethys_wps'}]
        ret = cli_docker_commands.get_docker_container_status(mock_dc)

        self.assertEquals(3, len(ret))
        self.assertTrue('tethys_postgis' in ret)
        self.assertTrue('tethys_geoserver' in ret)
        self.assertTrue('tethys_wps' in ret)
        self.assertTrue(ret['tethys_postgis'])
        self.assertTrue(ret['tethys_geoserver'])
        self.assertTrue(ret['tethys_wps'])

    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_get_docker_container_status_off(self, mock_dc):
        mock_dc.containers.return_value = [{'Names': ['/tethys_postgis'], 'Image': '/tethys_postgis'},
                                           {'Names': ['/tethys_geoserver'], 'Image': '/tethys_geoserver'}]
        ret = cli_docker_commands.get_docker_container_status(mock_dc)

        self.assertEquals(2, len(ret))
        self.assertTrue('tethys_postgis' in ret)
        self.assertTrue('tethys_geoserver' in ret)
        self.assertFalse('tethys_wps' in ret)
        self.assertTrue(ret['tethys_postgis'])
        self.assertTrue(ret['tethys_geoserver'])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_remove_docker_containers(self, mock_dc, mock_create, mock_pretty_output):
        mock_create.return_value = [{'Names': ['/tethys_postgis'], 'Image': '/tethys_postgis'},
                                    {'Names': ['/tethys_geoserver'], 'Image': '/tethys_geoserver'},
                                    {'Names': ['/tethys_wps'], 'Image': '/tethys_wps'}]
        cli_docker_commands.remove_docker_containers(mock_dc)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('Removing PostGIS...', po_call_args[0][0][0])
        self.assertEquals('Removing GeoServer...', po_call_args[1][0][0])
        self.assertEquals('Removing 52 North WPS...', po_call_args[2][0][0])
        mock_dc.remove_container.assert_any_call(container='tethys_postgis')
        mock_dc.remove_container.assert_any_call(container='tethys_geoserver', v=True)
        mock_dc.remove_container.assert_called_with(container='tethys_wps')

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.install_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.log_pull_stream')
    @mock.patch('tethys_apps.cli.docker_commands.get_images_to_install')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_init(self, mock_dc, mock_images, mock_stream, mock_containers, mock_pretty_output):
        mock_dc.return_value = mock.MagicMock()
        mock_images.return_value = ['foo_image', 'foo2']
        mock_stream.return_value = True
        mock_containers.return_value = True

        cli_docker_commands.docker_init()

        mock_dc.assert_called_once()
        mock_images.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('Pulling Docker images...', po_call_args[0][0][0])
        mock_stream.assert_called_with(mock_dc().pull())
        mock_containers.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'), defaults=False)

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.install_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.log_pull_stream')
    @mock.patch('tethys_apps.cli.docker_commands.get_images_to_install')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_init_no_images(self, mock_dc, mock_images, mock_stream, mock_containers, mock_pretty_output):
        mock_dc.return_value = mock.MagicMock()
        mock_images.return_value = []
        mock_stream.return_value = True
        mock_containers.return_value = True

        cli_docker_commands.docker_init()

        mock_dc.assert_called_once()
        mock_images.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('Docker images already pulled.', po_call_args[0][0][0])
        mock_stream.assert_not_called()
        mock_containers.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'), defaults=False)

    @mock.patch('tethys_apps.cli.docker_commands.start_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_start(self, mock_dc, mock_start):
        cli_docker_commands.docker_start(containers=('postgis', 'geoserver', 'wps'))

        mock_dc.assert_called_once()
        mock_start.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))

    @mock.patch('tethys_apps.cli.docker_commands.stop_boot2docker')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_stop(self, mock_dc, mock_stop, mock_boot):
        cli_docker_commands.docker_stop(containers=('postgis', 'geoserver', 'wps'))

        mock_dc.assert_called_once()
        mock_stop.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))
        mock_boot.assert_not_called()

    @mock.patch('tethys_apps.cli.docker_commands.stop_boot2docker')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_stop_boot2docker(self, mock_dc, mock_stop, mock_boot):
        cli_docker_commands.docker_stop(containers='', boot2docker=True)

        mock_dc.assert_called_once()
        mock_stop.assert_called_once_with(mock_dc(), containers='')
        mock_boot.assert_called_once()

    @mock.patch('tethys_apps.cli.docker_commands.start_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_restart(self, mock_dc, mock_stop, mock_start):
        cli_docker_commands.docker_restart()

        mock_dc.assert_called_once()
        mock_stop.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))
        mock_start.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))

    @mock.patch('tethys_apps.cli.docker_commands.start_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_restart_containers(self, mock_dc, mock_stop, mock_start):
        cli_docker_commands.docker_restart(containers=('postgis', 'geoserver'))

        mock_dc.assert_called_once()
        mock_stop.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver'))
        mock_start.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver'))

    @mock.patch('tethys_apps.cli.docker_commands.remove_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_remove(self, mock_dc, mock_stop, mock_remove):
        cli_docker_commands.docker_remove()

        mock_dc.assert_called_once()
        mock_stop.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))
        mock_remove.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))

    @mock.patch('tethys_apps.cli.docker_commands.remove_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_remove_containers(self, mock_dc, mock_stop, mock_remove):
        cli_docker_commands.docker_remove(containers=('postgis', 'geoserver'))

        mock_dc.assert_called_once()
        mock_stop.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver'))
        mock_remove.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver'))

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_status_container_running(self, mock_dc, mock_dc_status, mock_pretty_output):
        mock_dc_status.return_value = {'tethys_postgis': True, 'tethys_geoserver': True, 'tethys_wps': True}
        cli_docker_commands.docker_status()
        mock_dc.assert_called_once()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('PostGIS/Database: Running', po_call_args[0][0][0])
        self.assertEquals('GeoServer: Running', po_call_args[1][0][0])
        self.assertEquals('52 North WPS: Running', po_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_status_container_stopped(self, mock_dc, mock_dc_status, mock_pretty_output):
        mock_dc_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': False}
        cli_docker_commands.docker_status()
        mock_dc.assert_called_once()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('PostGIS/Database: Stopped', po_call_args[0][0][0])
        self.assertEquals('GeoServer: Stopped', po_call_args[1][0][0])
        self.assertEquals('52 North WPS: Stopped', po_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_status_container_not_installed(self, mock_dc, mock_dc_status, mock_pretty_output):
        mock_dc_status.return_value = {}
        cli_docker_commands.docker_status()
        mock_dc.assert_called_once()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('PostGIS/Database: Not Installed', po_call_args[0][0][0])
        self.assertEquals('GeoServer: Not Installed', po_call_args[1][0][0])
        self.assertEquals('52 North WPS: Not Installed', po_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.install_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.log_pull_stream')
    @mock.patch('tethys_apps.cli.docker_commands.remove_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_update_with_no_container(self, mock_dc, mock_stop, mock_remove, mock_lps, mock_install):
        cli_docker_commands.docker_update(containers=None, defaults=False)

        mock_dc.assert_called_once()

        mock_stop.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))

        mock_remove.assert_called_once_with(mock_dc(), containers=('postgis', 'geoserver', 'wps'))

        mock_lps.assert_any_call(mock_dc().pull())

        mock_install.assert_called_once_with(mock_dc(), force=True, containers=('postgis', 'geoserver', 'wps'),
                                             defaults=False)

    @mock.patch('tethys_apps.cli.docker_commands.install_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.log_pull_stream')
    @mock.patch('tethys_apps.cli.docker_commands.remove_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_update_with_container(self, mock_dc, mock_stop, mock_remove, mock_lps, mock_install):

        cli_docker_commands.docker_update(containers=[''], defaults=False)

        mock_dc.assert_called_once()

        mock_stop.assert_called_once_with(mock_dc(), containers=[''])

        mock_remove.assert_called_once_with(mock_dc(), containers=[''])

        mock_lps.assert_any_call(mock_dc().pull())

        mock_install.assert_called_once_with(mock_dc(), force=True, containers=[''], defaults=False)

    @mock.patch('tethys_apps.cli.docker_commands.install_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.log_pull_stream')
    @mock.patch('tethys_apps.cli.docker_commands.remove_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.stop_docker_containers')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_update_with_bad_container(self, mock_dc, mock_stop, mock_remove, mock_lps, mock_install):
        cli_docker_commands.docker_update(containers=['foo'], defaults=False)

        mock_dc.assert_called_once()

        mock_stop.assert_called_once_with(mock_dc(), containers=['foo'])

        mock_remove.assert_called_once_with(mock_dc(), containers=['foo'])

        mock_lps.assert_not_called()

        mock_install.assert_called_once_with(mock_dc(), force=True, containers=['foo'], defaults=False)

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_dicts')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_ip(self, mock_dc, mock_containers, mock_status, mock_pretty_output):
        mock_dc().host = 'host'

        mock_containers.return_value = {'tethys_postgis': {'Ports': [{'PublicPort': 123}]},
                                        'tethys_geoserver':  {'Ports': [{'PublicPort': 234}]},
                                        'tethys_wps': {'Ports': [{'PublicPort': 456}]}}

        mock_status.return_value = {'tethys_postgis': True, 'tethys_geoserver': True, 'tethys_wps': True}

        cli_docker_commands.docker_ip()

        mock_dc.assert_called()

        mock_containers.assert_called_once_with(mock_dc())

        mock_status.assert_called_once_with(mock_dc())

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(13, len(po_call_args))
        self.assertIn('PostGIS/Database:', po_call_args[0][0][0])
        self.assertEquals('  Host: host', po_call_args[1][0][0])
        self.assertEquals('  Port: 123', po_call_args[2][0][0])
        self.assertEquals('  Endpoint: postgresql://<username>:<password>@host:123/<database>', po_call_args[3][0][0])

        self.assertIn('GeoServer:', po_call_args[4][0][0])
        self.assertEquals('  Host: host', po_call_args[5][0][0])
        self.assertEquals('  Primary Port: 8181', po_call_args[6][0][0])
        self.assertEquals('  Node Ports: 234', po_call_args[7][0][0])
        self.assertEquals('  Endpoint: http://host:8181/geoserver/rest', po_call_args[8][0][0])

        self.assertIn('52 North WPS:', po_call_args[9][0][0])
        self.assertEquals('  Host: host', po_call_args[10][0][0])
        self.assertEquals('  Port: 456', po_call_args[11][0][0])
        self.assertEquals('  Endpoint: http://host:456/wps/WebProcessingService\n', po_call_args[12][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_dicts')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_ip_not_running(self, mock_dc, mock_containers, mock_status, mock_pretty_output):
        mock_dc().host = 'host'

        mock_containers.return_value = {'tethys_postgis': {'Ports': [{'PublicPort': 123}]},
                                        'tethys_geoserver': {'Ports': [{'PublicPort': 234}]},
                                        'tethys_wps': {'Ports': [{'PublicPort': 456}]}}

        mock_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': False}

        cli_docker_commands.docker_ip()

        mock_dc.assert_called()

        mock_containers.assert_called_once_with(mock_dc())

        mock_status.assert_called_once_with(mock_dc())

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('\nPostGIS/Database: Not Running.', po_call_args[0][0][0])
        self.assertEquals('\nGeoServer: Not Running.', po_call_args[1][0][0])
        self.assertEquals('\n52 North WPS: Not Running.', po_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_dicts')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_ip_not_installed(self, mock_dc, mock_containers, mock_status, mock_pretty_output):
        mock_dc().host = 'host'

        mock_containers.return_value = {'foo': {'Ports': [{'PublicPort': 123}]},
                                        'bar': {'Ports': [{'PublicPort': 234}]},
                                        'baz': {'Ports': [{'PublicPort': 456}]}}

        mock_status.return_value = {'foo': True, 'bar': True, 'baz': True}

        cli_docker_commands.docker_ip()

        mock_dc.assert_called()

        mock_containers.assert_called_once_with(mock_dc())

        mock_status.assert_called_once_with(mock_dc())

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('\nPostGIS/Database: Not Installed.', po_call_args[0][0][0])
        self.assertEquals('\nGeoServer: Not Installed.', po_call_args[1][0][0])
        self.assertEquals('\n52 North WPS: Not Installed.', po_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output.write')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_dicts')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_ip_exception_post_gis(self, mock_dc, mock_containers, mock_status, mock_pretty_output):
        mock_pretty_output.side_effect = Exception

        mock_dc().host = 'host'

        mock_containers.return_value = {'tethys_postgis': {'Ports': [{'PublicPort': 123}]},
                                        'tethys_geoserver': {'Ports': [{'PublicPort': 234}]},
                                        'tethys_wps': {'Ports': [{'PublicPort': 456}]}}

        mock_status.return_value = {'tethys_postgis': True, 'tethys_geoserver': False, 'tethys_wps': False}

        self.assertRaises(Exception, cli_docker_commands.docker_ip)

        mock_dc.assert_called()

        mock_containers.assert_called_once_with(mock_dc())

        mock_status.assert_called_once_with(mock_dc())

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output.write')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_dicts')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_ip_exception_geo_server(self, mock_dc, mock_containers, mock_status, mock_pretty_output):
        mock_pretty_output.side_effect = [True, Exception]

        mock_dc().host = 'host'

        mock_containers.return_value = {'tethys_postgis': {'Ports': [{'PublicPort': 123}]},
                                        'tethys_geoserver': {'Ports': [{'PublicPort': 234}]},
                                        'tethys_wps': {'Ports': [{'PublicPort': 456}]}}

        mock_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': True, 'tethys_wps': False}

        self.assertRaises(Exception, cli_docker_commands.docker_ip)

        mock_dc.assert_called()

        mock_containers.assert_called_once_with(mock_dc())

        mock_status.assert_called_once_with(mock_dc())

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output.write')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_dicts')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_client')
    def test_docker_ip_exception_wps(self, mock_dc, mock_containers, mock_status, mock_pretty_output):
        mock_pretty_output.side_effect = [True, True, Exception]
        mock_dc().host = 'host'
        mock_containers.return_value = {'tethys_postgis': {'Ports': [{'PublicPort': 123}]},
                                        'tethys_geoserver': {'Ports': [{'PublicPort': 234}]},
                                        'tethys_wps': {'Ports': [{'PublicPort': 456}]}}
        mock_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': True}

        self.assertRaises(Exception, cli_docker_commands.docker_ip)

        mock_dc.assert_called()
        mock_containers.assert_called_once_with(mock_dc())
        mock_status.assert_called_once_with(mock_dc())

    @mock.patch('tethys_apps.cli.docker_commands.docker_init')
    def test_docker_command_init(self, mock_function):
        mock_args = mock.MagicMock()
        mock_args.command = 'init'
        mock_args.containers = 'containers'
        mock_args.defaults = True
        mock_args.boot2docker = True

        cli_docker_commands.docker_command(mock_args)

        mock_function.assert_called_once_with(containers='containers', defaults=True)

    @mock.patch('tethys_apps.cli.docker_commands.docker_start')
    def test_docker_command_start(self, mock_function):
        mock_args = mock.MagicMock()
        mock_args.command = 'start'
        mock_args.containers = 'containers'
        mock_args.defaults = True
        mock_args.boot2docker = True

        cli_docker_commands.docker_command(mock_args)

        mock_function.assert_called_once_with(containers='containers')

    @mock.patch('tethys_apps.cli.docker_commands.docker_stop')
    def test_docker_command_stop(self, mock_function):
        mock_args = mock.MagicMock()
        mock_args.command = 'stop'
        mock_args.containers = 'containers'
        mock_args.defaults = True
        mock_args.boot2docker = True

        cli_docker_commands.docker_command(mock_args)

        mock_function.assert_called_once_with(containers='containers', boot2docker=True)

    @mock.patch('tethys_apps.cli.docker_commands.docker_status')
    def test_docker_command_status(self, mock_function):
        mock_args = mock.MagicMock()
        mock_args.command = 'status'
        mock_args.containers = 'containers'
        mock_args.defaults = True
        mock_args.boot2docker = True

        cli_docker_commands.docker_command(mock_args)

        mock_function.assert_called_once_with()

    @mock.patch('tethys_apps.cli.docker_commands.docker_update')
    def test_docker_command_update(self, mock_function):
        mock_args = mock.MagicMock()
        mock_args.command = 'update'
        mock_args.containers = 'containers'
        mock_args.defaults = True
        mock_args.boot2docker = True

        cli_docker_commands.docker_command(mock_args)

        mock_function.assert_called_once_with(containers='containers', defaults=True)

    @mock.patch('tethys_apps.cli.docker_commands.docker_remove')
    def test_docker_command_remove(self, mock_function):
        mock_args = mock.MagicMock()
        mock_args.command = 'remove'
        mock_args.containers = 'containers'
        mock_args.defaults = True
        mock_args.boot2docker = True

        cli_docker_commands.docker_command(mock_args)

        mock_function.assert_called_once_with(containers='containers')

    @mock.patch('tethys_apps.cli.docker_commands.docker_ip')
    def test_docker_command_ip(self, mock_function):
        mock_args = mock.MagicMock()
        mock_args.command = 'ip'
        mock_args.containers = 'containers'
        mock_args.defaults = True
        mock_args.boot2docker = True

        cli_docker_commands.docker_command(mock_args)

        mock_function.assert_called_once_with()

    @mock.patch('tethys_apps.cli.docker_commands.docker_restart')
    def test_docker_command_restart(self, mock_function):
        mock_args = mock.MagicMock()
        mock_args.command = 'restart'
        mock_args.containers = 'containers'
        mock_args.defaults = True
        mock_args.boot2docker = True

        cli_docker_commands.docker_command(mock_args)

        mock_function.assert_called_once_with(containers='containers')

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.getpass.getpass')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_postgis_password_given(self, mock_dc, mock_containers_to_create,
                                                              mock_getpass, mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_postgis']
        mock_getpass.side_effect = ['pass',  # tethys_default password
                                    'foo',  # tethys_default password not matching
                                    'pass',  # tethys_default password redo
                                    'pass',  # tethys_default password redo match
                                    'passmgr',  # tethys_db_manager password
                                    'foo',  # tethys_db_manager password not matching
                                    'passmgr',  # tethys_db_manager password redo
                                    'passmgr',  # tethys_db_manager password redo matching
                                    'passsuper',  # tethys_super password
                                    'foo',  # tethys_super password not matching
                                    'passsuper',  # tethys_super password redo
                                    'passsuper'  # tethys_super password redo matching
                                    ]
        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=False)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(6, len(po_call_args))
        self.assertEquals('\nInstalling the PostGIS Docker container...', po_call_args[0][0][0])
        self.assertIn('Provide passwords for the three Tethys database users or press enter', po_call_args[1][0][0])
        self.assertEquals('Passwords do not match, please try again: ', po_call_args[2][0][0])
        self.assertEquals('Passwords do not match, please try again: ', po_call_args[3][0][0])
        self.assertEquals('Passwords do not match, please try again: ', po_call_args[4][0][0])
        self.assertEquals('Finished installing Docker containers.', po_call_args[5][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.getpass.getpass')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_postgis_password_default(self, mock_dc, mock_containers_to_create,
                                                                mock_getpass, mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_postgis']
        mock_getpass.side_effect = ['',  # tethys_default password
                                    '',  # tethys_db_manager password
                                    '',  # tethys_super password
                                    ]
        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=False)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('\nInstalling the PostGIS Docker container...', po_call_args[0][0][0])
        self.assertIn('Provide passwords for the three Tethys database users or press enter', po_call_args[1][0][0])
        self.assertEquals('Finished installing Docker containers.', po_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.input')
    @mock.patch('tethys_apps.cli.docker_commands.create_host_config')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_geoserver_numprocessors_bind(self, mock_dc, mock_containers_to_create,
                                                                    mock_create_host_config, mock_input,
                                                                    mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_geoserver']
        mock_input.side_effect = ['1',  # Number of GeoServer Instances Enabled
                                  '1',  # Number of GeoServer Instances with REST API Enabled
                                  'c',  # Would you like to specify number of Processors (c) OR set limits (e)
                                  '2',  # Number of Processors
                                  '60',  # Maximum request timeout in seconds
                                  '1024',  # Maximum memory to allocate to each GeoServer instance in MB
                                  '0',  # Minimum memory to allocate to each GeoServer instance in MB
                                  'y',  # Bind the GeoServer data directory to the host?
                                  '/tmp'  # Specify location to bind data directory
                                  ]

        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=False)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(4, len(po_call_args))
        self.assertEquals('\nInstalling the GeoServer Docker container...', po_call_args[0][0][0])
        self.assertIn('The GeoServer docker can be configured to run in a clustered mode', po_call_args[1][0][0])
        self.assertIn('GeoServer can be configured with limits to certain types of requests', po_call_args[2][0][0])
        self.assertIn('Finished installing Docker containers', po_call_args[3][0][0])
        mock_create_host_config.assert_called()

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.input')
    @mock.patch('tethys_apps.cli.docker_commands.create_host_config')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_geoserver_limits_no_bind(self, mock_dc, mock_containers_to_create,
                                                                mock_create_host_config, mock_input,
                                                                mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_geoserver']
        mock_input.side_effect = ['1',  # Number of GeoServer Instances Enabled
                                  '1',  # Number of GeoServer Instances with REST API Enabled
                                  'e',  # Would you like to specify number of Processors (c) OR set limits (e)
                                  '100',  # Maximum number of simultaneous OGC web service requests
                                  '8',  # Maximum number of simultaneous GetMap requests
                                  '16',  # Maximum number of simultaneous GeoWebCache tile renders
                                  '60',  # Maximum request timeout in seconds
                                  '1024',  # Maximum memory to allocate to each GeoServer instance in MB
                                  '0',  # Minimum memory to allocate to each GeoServer instance in MB
                                  'n',  # Bind the GeoServer data directory to the host?
                                  ]

        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=False)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(4, len(po_call_args))
        self.assertEquals('\nInstalling the GeoServer Docker container...', po_call_args[0][0][0])
        self.assertIn('The GeoServer docker can be configured to run in a clustered mode', po_call_args[1][0][0])
        self.assertIn('GeoServer can be configured with limits to certain types of requests', po_call_args[2][0][0])
        self.assertIn('Finished installing Docker containers', po_call_args[3][0][0])
        mock_create_host_config.assert_not_called()

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.create_host_config')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_geoserver_defaults(self, mock_dc, mock_containers_to_create,
                                                          mock_create_host_config, mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_geoserver']

        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=True)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEquals('\nInstalling the GeoServer Docker container...', po_call_args[0][0][0])
        self.assertIn('Finished installing Docker containers', po_call_args[1][0][0])
        mock_create_host_config.assert_called_once_with(binds=['/usr/lib/tethys/geoserver/data:/var/geoserver/data'])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.GEOSERVER_IMAGE')
    @mock.patch('tethys_apps.cli.docker_commands.create_host_config')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_geoserver_no_cluster(self, mock_dc, mock_containers_to_create,
                                                            mock_create_host_config, mock_image, mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_geoserver']
        mock_image.return_value = ''

        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=True)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEquals('\nInstalling the GeoServer Docker container...', po_call_args[0][0][0])
        self.assertIn('Finished installing Docker containers', po_call_args[1][0][0])
        mock_create_host_config.assert_not_called()

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.getpass.getpass')
    @mock.patch('tethys_apps.cli.docker_commands.input')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_wps_no_defaults_password(self, mock_dc, mock_containers_to_create, mock_input,
                                                                mock_getpass, mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_wps']
        mock_input.side_effect = ['',  # Name
                                  '',  # Position
                                  '',  # Address
                                  '',  # City
                                  '',  # State
                                  '',  # Country
                                  '',  # Postal Code
                                  '',  # Email
                                  '',  # Phone
                                  '',  # Fax
                                  '']  # Admin username
        mock_getpass.side_effect = ['wps',  # Admin Password
                                    'foo',  # Admin Password no match
                                    'wps',  # Admin Password redo
                                    'wps']  # Admin Password match

        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=False)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(4, len(po_call_args))
        self.assertEquals('\nInstalling the 52 North WPS Docker container...', po_call_args[0][0][0])
        self.assertIn('Provide contact information for the 52 North Web Processing Service', po_call_args[1][0][0])
        self.assertEquals('Passwords do not match, please try again.', po_call_args[2][0][0])
        self.assertIn('Finished installing Docker containers', po_call_args[3][0][0])
        mock_dc.create_container.assert_called_once_with(name='tethys_wps',
                                                         image='ciwater/n52wps:3.3.1',
                                                         environment={'NAME': 'NONE',
                                                                      'POSITION': 'NONE',
                                                                      'ADDRESS': 'NONE',
                                                                      'CITY': 'NONE',
                                                                      'STATE': 'NONE',
                                                                      'COUNTRY': 'NONE',
                                                                      'POSTAL_CODE': 'NONE',
                                                                      'EMAIL': 'NONE',
                                                                      'PHONE': 'NONE',
                                                                      'FAX': 'NONE',
                                                                      'USERNAME': 'wps',
                                                                      'PASSWORD': 'wps'})

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.getpass.getpass')
    @mock.patch('tethys_apps.cli.docker_commands.input')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_wps_no_empty_defaults_blank_password(self, mock_dc, mock_containers_to_create,
                                                                            mock_input, mock_getpass,
                                                                            mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_wps']
        mock_input.side_effect = ['Name',  # Name
                                  'Pos',  # Position
                                  'Addr',  # Address
                                  'City',  # City
                                  'State',  # State
                                  'Cty',  # Country
                                  'Code',  # Postal Code
                                  'foo@foo.com',  # Email
                                  '123456789',  # Phone
                                  '123456788',  # Fax
                                  'fooadmin']  # Admin username
        mock_getpass.side_effect = ['']  # Admin Password

        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=False)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('\nInstalling the 52 North WPS Docker container...', po_call_args[0][0][0])
        self.assertIn('Provide contact information for the 52 North Web Processing Service', po_call_args[1][0][0])
        self.assertIn('Finished installing Docker containers', po_call_args[2][0][0])
        mock_dc.create_container.assert_called_once_with(name='tethys_wps',
                                                         image='ciwater/n52wps:3.3.1',
                                                         environment={'NAME': 'Name',
                                                                      'POSITION': 'Pos',
                                                                      'ADDRESS': 'Addr',
                                                                      'CITY': 'City',
                                                                      'STATE': 'State',
                                                                      'COUNTRY': 'Cty',
                                                                      'POSTAL_CODE': 'Code',
                                                                      'EMAIL': 'foo@foo.com',
                                                                      'PHONE': '123456789',
                                                                      'FAX': '123456788',
                                                                      'USERNAME': 'fooadmin',
                                                                      'PASSWORD': 'wps'})

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.getpass.getpass')
    @mock.patch('tethys_apps.cli.docker_commands.input')
    @mock.patch('tethys_apps.cli.docker_commands.get_containers_to_create')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_install_docker_containers_wps_defaults_password(self, mock_dc, mock_containers_to_create, mock_input,
                                                             mock_getpass, mock_pretty_output):
        mock_containers_to_create.return_value = ['tethys_wps']

        cli_docker_commands.install_docker_containers(mock_dc, force=False, defaults=True)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertEquals('\nInstalling the 52 North WPS Docker container...', po_call_args[0][0][0])
        self.assertIn('Finished installing Docker containers', po_call_args[1][0][0])
        mock_input.assert_not_called()
        mock_getpass.assert_not_called()
        mock_dc.create_container.assert_called_once_with(name='tethys_wps',
                                                         image='ciwater/n52wps:3.3.1',
                                                         environment={'NAME': 'NONE',
                                                                      'POSITION': 'NONE',
                                                                      'ADDRESS': 'NONE',
                                                                      'CITY': 'NONE',
                                                                      'STATE': 'NONE',
                                                                      'COUNTRY': 'NONE',
                                                                      'POSTAL_CODE': 'NONE',
                                                                      'EMAIL': 'NONE',
                                                                      'PHONE': 'NONE',
                                                                      'FAX': 'NONE',
                                                                      'USERNAME': 'wps',
                                                                      'PASSWORD': 'wps'})

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_image')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_start_docker_containers_already_running(self, mock_dc, mock_dc_image, mock_dc_status, mock_pretty_output):
        mock_dc_image.return_value = [{'Names': ['/tethys_postgis'], 'Image': '/tethys_postgis'},
                                      {'Names': ['/tethys_geoserver'], 'Image': '/tethys_geoserver'},
                                      {'Names': ['/tethys_wps'], 'Image': '/tethys_wps'}]
        mock_dc_status.return_value = {'tethys_postgis': True, 'tethys_geoserver': True, 'tethys_wps': True}

        cli_docker_commands.start_docker_containers(mock_dc)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('PostGIS container already running...', po_call_args[0][0][0])
        self.assertEquals('GeoServer container already running...', po_call_args[1][0][0])
        self.assertEquals('52 North WPS container already running...', po_call_args[2][0][0])
        mock_dc_image.assert_called_once_with(mock_dc)
        mock_dc_status.assert_called_with(mock_dc)

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_image')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_start_docker_containers_starting_cluster(self, mock_dc, mock_dc_image, mock_dc_status, mock_pretty_output):
        mock_dc_image.return_value = {'tethys_geoserver': 'cluster'}
        mock_dc_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': False}

        cli_docker_commands.start_docker_containers(mock_dc)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('Starting PostGIS container...', po_call_args[0][0][0])
        self.assertEquals('Starting GeoServer container...', po_call_args[1][0][0])
        self.assertEquals('Starting 52 North WPS container...', po_call_args[2][0][0])
        mock_dc_image.assert_called_once_with(mock_dc)
        mock_dc_status.assert_called_with(mock_dc)
        mock_dc.start.assert_any_call(container='tethys_postgis', port_bindings={5432: '5435'})
        mock_dc.start.assert_any_call(container='tethys_geoserver', port_bindings={8181: '8181',
                                                                                   8081: ('0.0.0.0', 8081),
                                                                                   8082: ('0.0.0.0', 8082),
                                                                                   8083: ('0.0.0.0', 8083),
                                                                                   8084: ('0.0.0.0', 8084)})
        mock_dc.start.assert_any_call(container='tethys_wps', port_bindings={8080: '8282'})

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_image')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_start_docker_containers_starting_no_cluster(self, mock_dc, mock_dc_image, mock_dc_status,
                                                         mock_pretty_output):
        mock_dc_image.return_value = {'tethys_geoserver': 'foo'}
        mock_dc_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': False}

        cli_docker_commands.start_docker_containers(mock_dc)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('Starting PostGIS container...', po_call_args[0][0][0])
        self.assertEquals('Starting GeoServer container...', po_call_args[1][0][0])
        self.assertEquals('Starting 52 North WPS container...', po_call_args[2][0][0])
        mock_dc_image.assert_called_once_with(mock_dc)
        mock_dc_status.assert_called_with(mock_dc)
        mock_dc.start.assert_any_call(container='tethys_postgis', port_bindings={5432: '5435'})
        mock_dc.start.assert_any_call(container='tethys_geoserver', port_bindings={8080: '8181'})
        mock_dc.start.assert_any_call(container='tethys_wps', port_bindings={8080: '8282'})

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_image')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_start_docker_containers_notinstalled(self, mock_dc, mock_dc_image, mock_dc_status,
                                                  mock_pretty_output):
        mock_dc_image.return_value = {'tethys_geoserver': 'foo'}
        mock_dc_status.return_value = {}

        cli_docker_commands.start_docker_containers(mock_dc)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('PostGIS container not installed...', po_call_args[0][0][0])
        self.assertEquals('GeoServer container not installed...', po_call_args[1][0][0])
        self.assertEquals('52 North WPS container not installed...', po_call_args[2][0][0])
        mock_dc_image.assert_called_once_with(mock_dc)
        mock_dc_status.assert_called_with(mock_dc)
        mock_dc.start.assert_not_called()

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_image')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_start_docker_containers_postgis_exception(self, mock_dc, mock_dc_image, mock_dc_status,
                                                       mock_pretty_output):
        mock_dc_image.return_value = {'tethys_geoserver': 'foo'}
        mock_dc_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': False}
        mock_dc.start.side_effect = Exception

        self.assertRaises(Exception, cli_docker_commands.start_docker_containers, mock_dc,
                          containers=['postgis'])

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('Starting PostGIS container...', po_call_args[0][0][0])
        mock_dc_image.assert_called_once_with(mock_dc)
        mock_dc_status.assert_called_with(mock_dc)
        mock_dc.start.assert_called_once()

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_image')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_start_docker_containers_geoserver_exception(self, mock_dc, mock_dc_image, mock_dc_status,
                                                         mock_pretty_output):
        mock_dc_image.return_value = {'tethys_geoserver': 'foo'}
        mock_dc_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': False}
        mock_dc.start.side_effect = Exception

        self.assertRaises(Exception, cli_docker_commands.start_docker_containers, mock_dc,
                          containers=['geoserver'])

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('Starting GeoServer container...', po_call_args[0][0][0])
        mock_dc_image.assert_called_once_with(mock_dc)
        mock_dc_status.assert_called_with(mock_dc)
        mock_dc.start.assert_called_once()

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_image')
    @mock.patch('tethys_apps.cli.docker_commands.DockerClient')
    def test_start_docker_containers_wps_exception(self, mock_dc, mock_dc_image, mock_dc_status, mock_pretty_output):
        mock_dc_image.return_value = {'tethys_geoserver': 'foo'}
        mock_dc_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': False}
        mock_dc.start.side_effect = Exception

        self.assertRaises(Exception, cli_docker_commands.start_docker_containers, mock_dc, containers=['wps'])

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('Starting 52 North WPS container...', po_call_args[0][0][0])
        mock_dc_image.assert_called_once_with(mock_dc)
        mock_dc_status.assert_called_with(mock_dc)
        mock_dc.start.assert_called_once()

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    def test_stop_docker_containers_already_stopped(self, mock_dc_status, mock_pretty_output):
        mock_docker_client = mock.MagicMock()
        mock_dc_status.return_value = {'tethys_postgis': False, 'tethys_geoserver': False, 'tethys_wps': False}

        cli_docker_commands.stop_docker_containers(mock_docker_client)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('PostGIS container already stopped.', po_call_args[0][0][0])
        self.assertEquals('GeoServer container already stopped.', po_call_args[1][0][0])
        self.assertEquals('52 North WPS container already stopped.', po_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    def test_stop_docker_containers_stopping(self, mock_dc_status, mock_pretty_output):
        mock_docker_client = mock.MagicMock()
        mock_docker_client.stop.return_value = True
        mock_dc_status.return_value = {'tethys_postgis': True, 'tethys_geoserver': True, 'tethys_wps': True}

        cli_docker_commands.stop_docker_containers(mock_docker_client)

        mock_docker_client.stop.assert_any_call(container='tethys_postgis')
        mock_docker_client.stop.assert_any_call(container='tethys_geoserver')
        mock_docker_client.stop.assert_any_call(container='tethys_wps')
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEquals('Stopping PostGIS container...', po_call_args[0][0][0])
        self.assertEquals('Stopping GeoServer container...', po_call_args[1][0][0])
        self.assertEquals('Stopping 52 North WPS container...', po_call_args[2][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.get_docker_container_status')
    def test_stop_docker_containers_not_installed(self, mock_dc_status, mock_pretty_output):
        mock_docker_client = mock.MagicMock()
        mock_docker_client.stop.side_effect = KeyError
        mock_dc_status.return_value = {'tethys_postgis': True, 'tethys_geoserver': True, 'tethys_wps': True}

        cli_docker_commands.stop_docker_containers(mock_docker_client)

        mock_docker_client.stop.assert_any_call(container='tethys_postgis')
        mock_docker_client.stop.assert_any_call(container='tethys_geoserver')
        mock_docker_client.stop.assert_any_call(container='tethys_wps')
        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(6, len(po_call_args))
        self.assertEquals('Stopping PostGIS container...', po_call_args[0][0][0])
        self.assertEquals('PostGIS container not installed...', po_call_args[1][0][0])
        self.assertEquals('Stopping GeoServer container...', po_call_args[2][0][0])
        self.assertEquals('GeoServer container not installed...', po_call_args[3][0][0])
        self.assertEquals('Stopping 52 North WPS container...', po_call_args[4][0][0])
        self.assertEquals('52 North WPS container not installed...', po_call_args[5][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.curses')
    @mock.patch('tethys_apps.cli.docker_commands.platform.system')
    def test_log_pull_stream_linux_with_id_bad_status(self, mock_platform_system, mock_curses, mock_pretty_output):
        mock_stream = ['{      "id":"358464",      "status":"foo",      "progress":"bar"   }']
        mock_platform_system.return_value = 'Linux'
        mock_curses.initscr().getmaxyx.return_value = 1, 80

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_any_call(0, 0, u'foo                                                   '
                                                           u'                         ')
        mock_curses.initscr().addstr.assert_called_with(1, 0, '---                                                 '
                                                              '                           ')
        mock_curses.initscr().refresh.assert_called_once()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.curses')
    @mock.patch('tethys_apps.cli.docker_commands.platform.system')
    def test_log_pull_stream_linux_with_id_progress_status(self, mock_platform_system, mock_curses, mock_pretty_output):
        mock_stream = ['{      "id":"358464",      "status":"Downloading",      "progress":"bar"   }']
        mock_platform_system.return_value = 'Linux'
        mock_curses.initscr().getmaxyx.return_value = 1, 80

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_called_with(0, 0, '358464: Downloading bar                             '
                                                              '                           ')
        mock_curses.initscr().refresh.assert_called_once()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.curses')
    @mock.patch('tethys_apps.cli.docker_commands.platform.system')
    def test_log_pull_stream_linux_with_id_status(self, mock_platform_system, mock_curses, mock_pretty_output):
        mock_stream = ['{      "id":"358464",      "status":"Downloading",      "progress":"bar"   }\r\n'
                       '{      "id":"358464",      "status":"Pulling fs layer",      "progress":"baz"   }']
        mock_platform_system.return_value = 'Linux'
        mock_curses.initscr().getmaxyx.return_value = 1, 80

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_called_with(0, 0, '358464: Downloading bar                             '
                                                              '                           ')
        mock_curses.initscr().refresh.assert_called()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.curses')
    @mock.patch('tethys_apps.cli.docker_commands.platform.system')
    def test_log_pull_stream_linux_with_no_id(self, mock_platform_system, mock_curses, mock_pretty_output):
        mock_stream = ['{      "status":"foo",      "progress":"bar"   }']
        mock_platform_system.return_value = 'Linux'
        mock_curses.initscr().getmaxyx.return_value = 1, 80

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_not_called()
        mock_curses.initscr().refresh.assert_not_called()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals(u'foo', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.pretty_output')
    @mock.patch('tethys_apps.cli.docker_commands.platform.system')
    def test_log_pull_stream_windows(self, mock_platform_system, mock_pretty_output):
        mock_stream = ['{      "id":"358464",      "status":"Downloading",      "progress":"bar"   }']
        mock_platform_system.return_value = 'Windows'

        cli_docker_commands.log_pull_stream(mock_stream)

        po_call_args = mock_pretty_output().__enter__().write.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEquals('358464:Downloading bar', po_call_args[0][0][0])

    @mock.patch('tethys_apps.cli.docker_commands.input')
    def test_validate_numeric_cli_input_second_empty_value(self, mock_input):
        mock_input.side_effect = ['']
        ret = cli_docker_commands.validate_numeric_cli_input(value='555', default=1, max=1)
        self.assertEqual('1', ret)

    @mock.patch('tethys_apps.cli.docker_commands.input')
    def test_validate_choice_cli_input_second_empty_value(self, mock_input):
        mock_input.side_effect = ['']
        ret = cli_docker_commands.validate_choice_cli_input(value='555', choices=['foo', 'bar'], default='foo')
        self.assertEqual('foo', ret)
