import unittest
from unittest import mock
import tethys_cli.docker_commands as cli_docker_commands
from pathlib import Path
from tempfile import gettempdir
import pytest
import sys


class TestDockerCommands(unittest.TestCase):
    def setUp(self):
        self.mock_dc = mock.MagicMock(name="docker_client")
        dc_patcher = mock.patch(
            "tethys_cli.docker_commands.docker.from_env", return_value=self.mock_dc
        )
        self.mock_from_env = dc_patcher.start()
        self.addCleanup(dc_patcher.stop)

        # this is required to reset the mock_dc on the docker commands module
        cli_docker_commands.ContainerMetadata.get_docker_client()

        input_patcher = mock.patch(
            "tethys_cli.docker_commands.input",
            return_value=mock.MagicMock(name="input"),
        )
        self.mock_input = input_patcher.start()
        self.addCleanup(input_patcher.stop)

    def tearDown(self):
        cli_docker_commands.ContainerMetadata._docker_client = None

    def make_args(
        self, command, num_containers=0, defaults=False, with_image_opts=False
    ):
        args = mock.Mock(
            command=command,
            containers=["c" for _ in range(num_containers)],
            defaults=defaults,
            image_name="some/image" if with_image_opts else None,
            image_tag="1.2.3" if with_image_opts else None,
        )
        return args

    def test_get_docker_client(self):
        dc = cli_docker_commands.ContainerMetadata.get_docker_client()
        self.assertIs(dc, self.mock_dc)

    def test_container_metadata_get_containers(self):
        all_containers = cli_docker_commands.ContainerMetadata.get_containers()
        self.assertEqual(4, len(all_containers))
        for container in all_containers:
            self.assertIsInstance(container, cli_docker_commands.ContainerMetadata)

    def test_container_metadata_get_containers_cached(self):
        mock_all_containers = mock.MagicMock()
        cli_docker_commands.ContainerMetadata.all_containers = mock_all_containers

        def cleanup():
            cli_docker_commands.ContainerMetadata.all_containers = None

        self.addCleanup(cleanup)
        all_containers = cli_docker_commands.ContainerMetadata.get_containers()
        self.assertIs(all_containers, mock_all_containers)
        cli_docker_commands.ContainerMetadata.all_containers = None

    def test_container_metadata_get_containers_with_containers_arg(self):
        containers_input = cli_docker_commands.docker_container_inputs

        for container_input in containers_input:
            containers = [container_input]
            all_containers = cli_docker_commands.ContainerMetadata.get_containers(
                containers=containers
            )
            self.assertEqual(
                1,
                len(all_containers),
                'Container input "{}" was not found in {}.'.format(
                    container_input, all_containers
                ),
            )
            self.assertEqual(container_input, all_containers[0].input)

    @mock.patch(
        "tethys_cli.docker_commands.ContainerMetadata.is_installed",
        new_callable=mock.PropertyMock,
    )
    def test_container_metadata_get_containers_with_installed(self, mock_is_installed):
        mock_is_installed.return_value = True
        all_containers = cli_docker_commands.ContainerMetadata.get_containers(
            installed=True
        )
        self.assertEqual(4, len(all_containers))
        all_containers = cli_docker_commands.ContainerMetadata.get_containers(
            installed=False
        )
        self.assertEqual(0, len(all_containers))

        mock_is_installed.return_value = False
        all_containers = cli_docker_commands.ContainerMetadata.get_containers(
            installed=True
        )
        self.assertEqual(0, len(all_containers))
        all_containers = cli_docker_commands.ContainerMetadata.get_containers(
            installed=False
        )
        self.assertEqual(4, len(all_containers))

    def test_container_metadata_get_containers_with_image_name_arg(self):
        all_containers = cli_docker_commands.ContainerMetadata.get_containers(
            containers=["thredds"], image_name="some/image"
        )
        self.assertEqual(1, len(all_containers))
        self.assertEqual("some/image", all_containers[0].image_name)

    def test_container_metadata_get_containers_with_image_tag_arg(self):
        all_containers = cli_docker_commands.ContainerMetadata.get_containers(
            containers=["thredds"], image_name="1.2.3"
        )
        self.assertEqual(1, len(all_containers))
        self.assertEqual("1.2.3", all_containers[0].image_name)

    @mock.patch(
        "tethys_cli.docker_commands.ContainerMetadata.container",
        new_callable=mock.PropertyMock,
    )
    def test_container_metadata_is_installed(self, mock_container):
        mock_container.return_value = None
        cm = cli_docker_commands.PostGisContainerMetadata()
        self.assertFalse(cm.is_installed)

        mock_container.return_value = mock.Mock()
        self.assertTrue(cm.is_installed)

    def test_container_metadata_container(self):
        mock_container = mock.MagicMock()
        self.mock_dc.containers.get.return_value = mock_container
        cm = cli_docker_commands.PostGisContainerMetadata()
        self.assertEqual(mock_container, cm.container)

    def test_container_metadata_container_exception(self):
        self.mock_dc.containers.get.side_effect = cli_docker_commands.DockerNotFound(
            "test"
        )
        cm = cli_docker_commands.PostGisContainerMetadata()
        self.assertIsNone(cm.container)

    def test_container_metadata_container_cached(self):
        mock_container = mock.MagicMock()
        cm = cli_docker_commands.PostGisContainerMetadata()
        cm._container = mock_container
        self.assertEqual(mock_container, cm.container)

    def test_container_metadata_init(self):
        cli_docker_commands.PostGisContainerMetadata()

    def test_container_metadata_init_with_docker_client_arg(self):
        mock_dc = mock.MagicMock()
        c = cli_docker_commands.PostGisContainerMetadata(mock_dc)
        self.assertIs(c._docker_client, mock_dc)

    def test_port_bindings_postgis(self):
        cm = cli_docker_commands.PostGisContainerMetadata()
        self.assertDictEqual({5432: 5435}, cm.port_bindings)

    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.is_cluster",
        new_callable=mock.PropertyMock,
    )
    def test_port_bindings_geoserver(self, mock_is_cluster):
        mock_is_cluster.return_value = True
        cm = cli_docker_commands.GeoServerContainerMetadata()
        self.assertDictEqual(
            {
                8181: 8181,
                8081: 8081,
                8082: 8082,
                8083: 8083,
                8084: 8084,
            },
            cm.port_bindings,
        )

    def test_port_bindings_geoserver_non_clustered(self):
        cm = cli_docker_commands.GeoServerContainerMetadata()
        self.assertDictEqual({8080: 8181}, cm.port_bindings)

    def test_port_bindings_52_north(self):
        cm = cli_docker_commands.N52WpsContainerMetadata()
        self.assertDictEqual({8080: 8282}, cm.port_bindings)

    def test_port_bindings_thredds(self):
        cm = cli_docker_commands.ThreddsContainerMetadata()
        self.assertDictEqual({8080: 8383}, cm.port_bindings)

    def test_cm_ip_postgis(self):
        cm = cli_docker_commands.PostGisContainerMetadata()
        expected_msg = (
            "\nPostGIS/Database:"
            "\n  Host: 127.0.0.1"
            "\n  Port: 5435"
            "\n  Endpoint: postgresql://<username>:<password>@127.0.0.1:5435/<database>"
        )
        self.assertEqual(expected_msg, cm.ip)

    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.is_cluster",
        new_callable=mock.PropertyMock,
    )
    def test_cm_ip_geoserver(self, mock_is_cluster):
        mock_is_cluster.return_value = True
        cm = cli_docker_commands.GeoServerContainerMetadata()
        expected_msg = (
            "\nGeoServer:"
            "\n  Host: 127.0.0.1"
            "\n  Primary Port: 8181"
            "\n  Node Ports: 8081, 8082, 8083, 8084"
            "\n  Endpoint: http://127.0.0.1:8181/geoserver/rest"
        )
        self.assertEqual(expected_msg, cm.ip)

    def test_cm_ip_geoserver_non_clustered(self):
        cm = cli_docker_commands.GeoServerContainerMetadata()
        expected_msg = (
            "\nGeoServer:"
            "\n  Host: 127.0.0.1"
            "\n  Port: 8181"
            "\n  Endpoint: http://127.0.0.1:8181/geoserver/rest"
        )
        self.assertEqual(expected_msg, cm.ip)

    def test_cm_ip_52_north(self):
        cm = cli_docker_commands.N52WpsContainerMetadata()
        expected_msg = (
            "\n52 North WPS:"
            "\n  Host: 127.0.0.1"
            "\n  Port: 8282"
            "\n  Endpoint: http://127.0.0.1:8282/wps/WebProcessingService"
        )
        self.assertEqual(expected_msg, cm.ip)

    def test_cm_ip_thredds(self):
        cm = cli_docker_commands.ThreddsContainerMetadata()
        expected_msg = (
            "\nTHREDDS:"
            "\n  Host: 127.0.0.1"
            "\n  Port: 8383"
            "\n  Endpoint: http://127.0.0.1:8383/thredds/"
        )
        self.assertEqual(expected_msg, cm.ip)

    @mock.patch(
        "tethys_cli.docker_commands.ContainerMetadata.port_bindings",
        new_callable=mock.PropertyMock,
    )
    def test_cm_default_container_options_postgis(self, mock_port_bindings_prop):
        mock_port_bindings = mock.Mock()
        mock_port_bindings_prop.return_value = mock_port_bindings
        expected_options = dict(
            name="tethys_postgis",
            image="postgis/postgis:latest",
            environment=dict(
                POSTGRES_PASSWORD="mysecretpassword",
            ),
            host_config=dict(port_bindings=mock_port_bindings),
        )
        container = cli_docker_commands.PostGisContainerMetadata()
        self.assertDictEqual(expected_options, container.default_container_options())

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_verified_password")
    @mock.patch(
        "tethys_cli.docker_commands.PostGisContainerMetadata.default_container_options"
    )
    def test_cm_get_container_options_postgis(
        self, mock_default_options, mock_getpass, mock_pretty_output
    ):
        mock_default_options.return_value = dict(
            environment=dict(POSTGRES_PASSWORD="mysecretpassword")
        )
        mock_getpass.side_effect = [
            "pass",  # POSTGRES_PASSWORD
        ]

        expected_environment = dict(
            POSTGRES_PASSWORD="pass",
        )

        container = cli_docker_commands.PostGisContainerMetadata()
        self.assertDictEqual(
            expected_environment,
            container.get_container_options(defaults=False)["environment"],
        )

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Tethys uses the postgis/postgis image on Docker Hub. "
            "See: https://hub.docker.com/r/postgis/postgis/",
            po_call_args[0][0][0],
        )
        mock_default_options.assert_called()

    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.port_bindings",
        new_callable=mock.PropertyMock,
    )
    def test_cm_default_container_options_geoserver(self, mock_port_bindings_prop):
        mock_port_bindings = mock.Mock()
        mock_port_bindings_prop.return_value = mock_port_bindings
        expected_options = dict(
            name="tethys_geoserver",
            image="tethysplatform/geoserver:latest",
            environment=dict(
                ENABLED_NODES="1",
                REST_NODES="1",
                MAX_TIMEOUT="60",
                NUM_CORES="4",
                MAX_MEMORY="1024",
                MIN_MEMORY="1024",
            ),
            volumes=[
                "/var/log/supervisor:rw",
                "/var/geoserver/data:rw",
                "/var/geoserver:rw",
            ],
            host_config=dict(port_bindings=mock_port_bindings),
        )
        container = cli_docker_commands.GeoServerContainerMetadata()
        self.assertDictEqual(expected_options, container.default_container_options())

    @mock.patch("tethys_cli.docker_commands.Mount")
    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_valid_numeric_input")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_valid_choice_input")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_valid_directory_input")
    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.default_container_options"
    )
    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.is_cluster",
        new_callable=mock.PropertyMock,
    )
    def test_cm_get_container_options_geoserver_numprocessors_bind(
        self,
        mock_is_cluster,
        mock_default_options,
        mock_dir_input,
        mock_choice_input,
        mock_numeric_input,
        mock_pretty_output,
        mock_mount,
    ):
        mock_is_cluster.return_value = True
        mock_default_options.return_value = dict(environment={}, host_config={})
        mock_mount.return_value = mock.Mock()
        mock_numeric_input.side_effect = [
            "1",  # Number of GeoServer Instances Enabled
            "1",  # Number of GeoServer Instances with REST API Enabled
            "2",  # Number of Processors
            "60",  # Maximum request timeout in seconds
            "1024",  # Maximum memory to allocate to each GeoServer instance in MB
            "0",  # Minimum memory to allocate to each GeoServer instance in MB
        ]
        mock_choice_input.side_effect = [
            "c",  # Would you like to specify number of Processors (c) OR set limits (e)
            "y",  # Bind the GeoServer data directory to the host?
        ]
        mock_dir_input.side_effect = [
            gettempdir()
        ]  # Specify location to bind data directory

        expected_options = dict(
            environment=dict(
                ENABLED_NODES="1",
                REST_NODES="1",
                MAX_TIMEOUT="60",
                NUM_CORES="2",
                MAX_MEMORY="1024",
                MIN_MEMORY="0",
            ),
            host_config=dict(mounts=[mock_mount.return_value]),
        )

        container = cli_docker_commands.GeoServerContainerMetadata()
        self.assertDictEqual(
            expected_options, container.get_container_options(defaults=False)
        )

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn(
            "The GeoServer docker can be configured to run in a clustered mode",
            po_call_args[0][0][0],
        )
        self.assertIn(
            "GeoServer can be configured with limits to certain types of requests",
            po_call_args[1][0][0],
        )

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_valid_numeric_input")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_valid_choice_input")
    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.default_container_options"
    )
    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.is_cluster",
        new_callable=mock.PropertyMock,
    )
    def test_cm_get_container_options_geoserver_limits_no_bind(
        self,
        mock_is_cluster,
        mock_default_options,
        mock_choice_input,
        mock_numeric_input,
        mock_pretty_output,
    ):
        mock_is_cluster.return_value = True
        mock_default_options.return_value = dict(environment={}, host_config={})
        mock_numeric_input.side_effect = [
            "1",  # Number of GeoServer Instances Enabled
            "1",  # Number of GeoServer Instances with REST API Enabled
            "100",  # Maximum number of simultaneous OGC web service requests
            "8",  # Maximum number of simultaneous GetMap requests
            "16",  # Maximum number of simultaneous GeoWebCache tile renders
            "60",  # Maximum request timeout in seconds
            "1024",  # Maximum memory to allocate to each GeoServer instance in MB
            "0",  # Minimum memory to allocate to each GeoServer instance in MB
        ]
        mock_choice_input.side_effect = [
            "e",  # Would you like to specify number of Processors (c) OR set limits (e)
            "n",  # Bind the GeoServer data directory to the host?
        ]

        expected_options = dict(
            environment=dict(
                ENABLED_NODES="1",
                REST_NODES="1",
                MAX_TIMEOUT="60",
                MAX_MEMORY="1024",
                MIN_MEMORY="0",
                MAX_OWS_GLOBAL="100",
                MAX_WMS_GETMAP="8",
                MAX_OWS_GWC="16",
            ),
            host_config={},
        )

        container = cli_docker_commands.GeoServerContainerMetadata()
        actual_options = container.get_container_options(defaults=False)
        self.assertDictEqual(expected_options, actual_options)
        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(2, len(po_call_args))
        self.assertIn(
            "The GeoServer docker can be configured to run in a clustered mode",
            po_call_args[0][0][0],
        )
        self.assertIn(
            "GeoServer can be configured with limits to certain types of requests",
            po_call_args[1][0][0],
        )

    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.default_container_options"
    )
    def test_cm_get_container_options_geoserver_defaults(self, mock_default_options):
        mock_default_options.return_value = mock.Mock()

        container = cli_docker_commands.GeoServerContainerMetadata()
        self.assertEqual(
            mock_default_options.return_value,
            container.get_container_options(defaults=False),
        )
        mock_default_options.assert_called()

    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.is_cluster",
        new_callable=mock.PropertyMock,
    )
    @mock.patch(
        "tethys_cli.docker_commands.GeoServerContainerMetadata.default_container_options"
    )
    def test_cm_get_container_options_geoserver_no_cluster(
        self, mock_default_options, mock_is_cluster
    ):
        mock_default_options.return_value = dict()
        mock_is_cluster.return_value = False

        container = cli_docker_commands.GeoServerContainerMetadata()
        self.assertEqual(
            mock_default_options.return_value,
            container.get_container_options(defaults=False),
        )
        mock_default_options.assert_called()
        mock_is_cluster.assert_called()

    @mock.patch(
        "tethys_cli.docker_commands.ContainerMetadata.port_bindings",
        new_callable=mock.PropertyMock,
    )
    def test_cm_default_container_options_52_north(self, mock_port_bindings_prop):
        mock_port_bindings = mock.Mock()
        mock_port_bindings_prop.return_value = mock_port_bindings
        expected_options = dict(
            name="tethys_wps",
            image="ciwater/n52wps:3.3.1",
            environment=dict(
                NAME="NONE",
                POSITION="NONE",
                ADDRESS="NONE",
                CITY="NONE",
                STATE="NONE",
                COUNTRY="NONE",
                POSTAL_CODE="NONE",
                EMAIL="NONE",
                PHONE="NONE",
                FAX="NONE",
                USERNAME="wps",
                PASSWORD="wps",
            ),
            host_config=dict(port_bindings=mock_port_bindings),
        )
        container = cli_docker_commands.N52WpsContainerMetadata()
        self.assertDictEqual(expected_options, container.default_container_options())

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_verified_password")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_input_with_default")
    @mock.patch(
        "tethys_cli.docker_commands.ContainerMetadata.default_container_options"
    )
    def test_cm_get_container_options_52_north(
        self, mock_default_options, mock_input, mock_getpass, mock_pretty_output
    ):
        mock_default_options.return_value = dict(environment={})
        mock_input.side_effect = [
            "Name",  # Name
            "Pos",  # Position
            "Addr",  # Address
            "City",  # City
            "State",  # State
            "Cty",  # Country
            "Code",  # Postal Code
            "foo@foo.com",  # Email
            "123456789",  # Phone
            "123456788",  # Fax
            "fooadmin",  # Admin username
        ]
        mock_getpass.side_effect = ["wps"]  # Admin Password

        expected_options = dict(
            environment={
                "NAME": "Name",
                "POSITION": "Pos",
                "ADDRESS": "Addr",
                "CITY": "City",
                "STATE": "State",
                "COUNTRY": "Cty",
                "POSTAL_CODE": "Code",
                "EMAIL": "foo@foo.com",
                "PHONE": "123456789",
                "FAX": "123456788",
                "USERNAME": "fooadmin",
                "PASSWORD": "wps",
            },
        )

        container = cli_docker_commands.N52WpsContainerMetadata()
        self.assertDictEqual(
            expected_options, container.get_container_options(defaults=False)
        )

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "Provide contact information for the 52 North Web Processing Service",
            po_call_args[0][0][0],
        )
        mock_default_options.assert_called()

    @mock.patch(
        "tethys_cli.docker_commands.ContainerMetadata.port_bindings",
        new_callable=mock.PropertyMock,
    )
    def test_cm_default_container_options_thredds(self, mock_port_bindings_prop):
        mock_port_bindings = mock.Mock()
        mock_port_bindings_prop.return_value = mock_port_bindings
        expected_options = dict(
            name="tethys_thredds",
            image="unidata/thredds-docker:5.6",
            environment=dict(
                TDM_PW="CHANGEME!",
                TDS_HOST="http://localhost",
                THREDDS_XMX_SIZE="4G",
                THREDDS_XMS_SIZE="1G",
                TDM_XMX_SIZE="6G",
                TDM_XMS_SIZE="1G",
            ),
            volumes=["/usr/local/tomcat/content/thredds:rw"],
            host_config=dict(port_bindings=mock_port_bindings),
        )
        container = cli_docker_commands.ThreddsContainerMetadata()
        self.assertDictEqual(expected_options, container.default_container_options())

    @mock.patch("tethys_cli.docker_commands.Mount")
    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_valid_directory_input")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_valid_choice_input")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_verified_password")
    @mock.patch("tethys_cli.docker_commands.UserInputHelper.get_input_with_default")
    @mock.patch(
        "tethys_cli.docker_commands.ContainerMetadata.default_container_options"
    )
    def test_cm_get_container_options_thredds(
        self,
        mock_default_options,
        mock_input,
        mock_getpass,
        mock_choice_input,
        mock_dir_input,
        mock_pretty_output,
        mock_mount,
    ):
        mock_default_options.return_value = dict(environment={}, host_config={})

        mock_getpass.side_effect = ["please-dont-use-default-passwords"]  # TDM Password

        mock_input.side_effect = [
            "https://example.com",  # TDS Host
            "6G",  # THREDDS XMX
            "2G",  # THREDDS XMS
            "8G",  # TDM XMX
            "3G",  # TDM XMS
        ]

        mock_choice_input.side_effect = [
            "y",  # Bind the THREDDS data directory to the host?
        ]

        mock_dir_input.side_effect = [
            gettempdir()
        ]  # Specify location to bind data directory

        expected_options = dict(
            environment=dict(
                TDM_PW="please-dont-use-default-passwords",
                TDS_HOST="https://example.com",
                THREDDS_XMX_SIZE="6G",
                THREDDS_XMS_SIZE="2G",
                TDM_XMX_SIZE="8G",
                TDM_XMS_SIZE="3G",
            ),
            host_config=dict(mounts=[mock_mount.return_value]),
            volumes=["/usr/local/tomcat/content/thredds:rw"],
        )

        container = cli_docker_commands.ThreddsContainerMetadata()
        self.assertDictEqual(
            expected_options, container.get_container_options(defaults=False)
        )

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Provide configuration options for the THREDDS container or or press enter to accept the "
            "defaults shown in square brackets: ",
            po_call_args[0][0][0],
        )
        mock_default_options.assert_called()

    @mock.patch("tethys_cli.docker_commands.log_pull_stream")
    @mock.patch(
        "tethys_cli.docker_commands.PostGisContainerMetadata.image",
        new_callable=mock.PropertyMock,
    )
    def test_cm_pull(self, mock_image, mock_pull_stream):
        container = cli_docker_commands.PostGisContainerMetadata()
        container.pull()
        self.mock_dc.api.pull.assert_called_with(mock_image.return_value, stream=True)
        mock_pull_stream.assert_called()

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch(
        "tethys_cli.docker_commands.PostGisContainerMetadata.get_container_options"
    )
    def test_cm_create(self, mock_get_options, mock_pretty_output):
        mock_get_options.return_value = dict(host_config={})

        container = cli_docker_commands.PostGisContainerMetadata()
        container.create()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn(
            "\nInstalling the PostGIS/Database Docker container...",
            po_call_args[0][0][0],
        )
        mock_get_options.assert_called_with(False)
        self.mock_dc.api.create_host_config.assert_called_with()
        self.mock_dc.api.create_container.assert_called()

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    def test_cm_start(self, mock_pretty_output):
        container = cli_docker_commands.PostGisContainerMetadata()
        msg = container.start()
        self.assertIsNone(msg)

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Starting PostGIS/Database container...", po_call_args[0][0][0])
        self.mock_dc.containers.get().start.assert_called()

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    def test_cm_start_exception(self, mock_pretty_output):
        self.mock_dc.containers.get().start.side_effect = Exception
        container = cli_docker_commands.PostGisContainerMetadata()
        msg = container.start()
        self.assertIn("There was an error while attempting to start container", msg)

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Starting PostGIS/Database container...", po_call_args[0][0][0])
        self.mock_dc.containers.get().start.assert_called()

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    def test_cm_stop(self, mock_pretty_output):
        container = cli_docker_commands.PostGisContainerMetadata()
        msg = container.stop()
        self.assertIsNone(msg)

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Stopping PostGIS/Database container...", po_call_args[0][0][0])
        self.mock_dc.containers.get().stop.assert_called()

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    def test_cm_stop_exception(self, mock_pretty_output):
        self.mock_dc.containers.get().stop.side_effect = Exception
        container = cli_docker_commands.PostGisContainerMetadata()
        msg = container.stop()
        self.assertIn("There was an error while attempting to stop container", msg)

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Stopping PostGIS/Database container...", po_call_args[0][0][0])
        self.mock_dc.containers.get().stop.assert_called()

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    def test_cm_remove(self, mock_pretty_output):
        container = cli_docker_commands.PostGisContainerMetadata()
        container.remove()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertIn("Removing PostGIS/Database container...", po_call_args[0][0][0])
        self.mock_dc.containers.get().remove.assert_called()

    @mock.patch("tethys_cli.docker_commands.ContainerMetadata.get_containers")
    def test_get_docker_container_statuses(self, mock_get_containers):
        mock_containers = [mock.MagicMock() for _ in range(3)]
        mock_get_containers.return_value = mock_containers

        self.mock_dc.containers.list.return_value = mock_containers

        ret = cli_docker_commands.get_docker_container_statuses()

        self.assertEqual(3, len(ret))
        for status in ret.values():
            self.assertTrue(status)

    @mock.patch("tethys_cli.docker_commands.ContainerMetadata.get_containers")
    def test_get_docker_container_statuses_off(self, mock_get_containers):
        mock_containers = [mock.MagicMock() for _ in range(3)]
        mock_get_containers.return_value = mock_containers

        self.mock_dc.containers.list.side_effect = [
            mock_containers,
            mock_containers[:2],
        ]

        ret = cli_docker_commands.get_docker_container_statuses()

        self.assertEqual(3, len(ret))
        self.assertTrue(ret[mock_containers[0]])
        self.assertTrue(ret[mock_containers[1]])
        self.assertFalse(ret[mock_containers[2]])

    @mock.patch("tethys_cli.docker_commands.ContainerMetadata.get_containers")
    def test_get_docker_container_statuses_not_installed(self, mock_get_containers):
        mock_containers = [mock.MagicMock() for _ in range(3)]
        mock_get_containers.return_value = mock_containers

        self.mock_dc.containers.list.side_effect = [
            mock_containers[:2],
            mock_containers[:1],
        ]

        ret = cli_docker_commands.get_docker_container_statuses()

        self.assertEqual(3, len(ret))
        self.assertTrue(ret[mock_containers[0]])
        self.assertFalse(ret[mock_containers[1]])
        self.assertIsNone(ret[mock_containers[2]])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    def test_pull_docker_images(self, mock_pretty_output):
        mock_container = mock.Mock()
        cli_docker_commands.pull_docker_images([mock_container])
        mock_container.pull.assert_called_once()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual("Pulling Docker images...", po_call_args[0][0][0])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    def test_pull_docker_images_already_pulled(self, mock_pretty_output):
        cli_docker_commands.pull_docker_images([])

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual("Docker images already pulled.", po_call_args[0][0][0])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    def test_install_docker_containers(self, mock_pretty_output):
        mock_container = mock.Mock()
        cli_docker_commands.install_docker_containers([mock_container])
        mock_container.create.assert_called_once_with(False)

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Finished installing Docker containers.", po_call_args[0][0][0]
        )

    @mock.patch("tethys_cli.docker_commands.install_docker_containers")
    @mock.patch("tethys_cli.docker_commands.pull_docker_images")
    @mock.patch("tethys_cli.docker_commands.ContainerMetadata.get_containers")
    def test_docker_init(self, mock_get_containers, mock_pull, mock_install):
        mock_get_containers.return_value = mock.Mock()
        cli_docker_commands.docker_init()
        mock_get_containers.assert_called_with(
            None, installed=False, image_name=None, image_tag=None
        )

        mock_pull.assert_called_with(mock_get_containers.return_value)
        mock_install.assert_called_with(
            mock_get_containers.return_value, defaults=False
        )

        cli_docker_commands.docker_init(force=True)
        mock_get_containers.assert_called_with(
            None, installed=None, image_name=None, image_tag=None
        )

        mock_pull.assert_called_with(mock_get_containers.return_value)
        mock_install.assert_called_with(
            mock_get_containers.return_value, defaults=False
        )

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.get_docker_container_statuses")
    def test_docker_start(self, mock_dc_status, mock_pretty_output):
        mock_container = mock.Mock()
        mock_container.start.return_value = "{} starting"
        mock_container.display_name = "Mock"
        mock_dc_status.return_value = mock.Mock()
        mock_dc_status.return_value.items.return_value = [
            (mock_container, None),
            (mock_container, True),
            (mock_container, False),
        ]
        cli_docker_commands.docker_start()
        mock_container.start.assert_called()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertIn("Mock container not installed.", po_call_args[0][0][0])
        self.assertIn("Mock container already running.", po_call_args[1][0][0])
        self.assertIn("Mock starting", po_call_args[2][0][0])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.get_docker_container_statuses")
    def test_docker_stop(self, mock_dc_status, mock_pretty_output):
        mock_container = mock.Mock()
        mock_container.stop.return_value = "{} stopping"
        mock_container.display_name = "Mock"
        mock_dc_status.return_value = mock.Mock()
        mock_dc_status.return_value.items.return_value = [
            (mock_container, None),
            (mock_container, False),
            (mock_container, True),
        ]
        cli_docker_commands.docker_stop()
        mock_container.stop.assert_called()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEqual("Mock container not installed.", po_call_args[0][0][0])
        self.assertEqual("Mock container already stopped.", po_call_args[1][0][0])
        self.assertEqual("Mock stopping", po_call_args[2][0][0])

    @mock.patch("tethys_cli.docker_commands.docker_start")
    @mock.patch("tethys_cli.docker_commands.docker_stop")
    def test_docker_restart(self, mock_stop, mock_start):
        containers = mock.Mock()
        cli_docker_commands.docker_restart(containers)
        mock_stop.assert_called_with(containers=containers)
        mock_start.assert_called_with(containers=containers)

    @mock.patch("tethys_cli.docker_commands.ContainerMetadata.get_containers")
    @mock.patch("tethys_cli.docker_commands.docker_stop")
    def test_docker_remove(self, mock_stop, mock_get_containers):
        containers = mock.Mock()
        mock_get_containers.return_value = [containers]
        cli_docker_commands.docker_remove(containers)
        mock_stop.assert_called_with(containers=containers)
        mock_get_containers.assert_called_with(containers, installed=True)
        containers.remove.assert_called()

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.get_docker_container_statuses")
    def test_docker_status(self, mock_dc_status, mock_pretty_output):
        mock_container = mock.Mock()
        mock_container.display_name = "Mock"
        mock_dc_status.return_value = mock.Mock()
        mock_dc_status.return_value.items.return_value = [
            (mock_container, None),
            (mock_container, True),
            (mock_container, False),
        ]
        cli_docker_commands.docker_status()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEqual("Mock: Not Installed", po_call_args[0][0][0])
        self.assertEqual("Mock: Running", po_call_args[1][0][0])
        self.assertEqual("Mock: Not Running", po_call_args[2][0][0])

    @mock.patch("tethys_cli.docker_commands.docker_init")
    @mock.patch("tethys_cli.docker_commands.docker_remove")
    def test_docker_update(self, mock_remove, mock_init):
        containers = mock.Mock()
        cli_docker_commands.docker_update(containers)
        mock_remove.assert_called_with(containers=containers)
        mock_init.assert_called_with(
            containers=containers,
            defaults=False,
            force=True,
            image_name=None,
            image_tag=None,
        )

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.get_docker_container_statuses")
    def test_docker_ip(self, mock_dc_status, mock_pretty_output):
        mock_container = mock.Mock()
        mock_container.configure_mock(ip="{name}: ip data")
        mock_container.display_name = "Mock"
        mock_dc_status.return_value = mock.Mock()
        mock_dc_status.return_value.items.return_value = [
            (mock_container, None),
            (mock_container, False),
            (mock_container, True),
        ]
        cli_docker_commands.docker_ip()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(3, len(po_call_args))
        self.assertEqual("Mock: Not Installed", po_call_args[0][0][0])
        self.assertEqual("Mock: Not Running", po_call_args[1][0][0])
        self.assertEqual("Mock: ip data", po_call_args[2][0][0])

    @mock.patch("tethys_cli.docker_commands.docker_restart")
    @mock.patch("tethys_cli.docker_commands.docker_ip")
    @mock.patch("tethys_cli.docker_commands.docker_remove")
    @mock.patch("tethys_cli.docker_commands.docker_update")
    @mock.patch("tethys_cli.docker_commands.docker_status")
    @mock.patch("tethys_cli.docker_commands.docker_stop")
    @mock.patch("tethys_cli.docker_commands.docker_start")
    @mock.patch("tethys_cli.docker_commands.docker_init")
    def test_docker_command(
        self,
        mock_init,
        mock_start,
        mock_stop,
        mock_status,
        mock_update,
        mock_remove,
        mock_ip,
        mock_restart,
    ):
        args = self.make_args("init", with_image_opts=True)
        cli_docker_commands.docker_command(args)
        mock_init.assert_called_with(
            containers=args.containers,
            defaults=args.defaults,
            image_name=args.image_name,
            image_tag=args.image_tag,
        )
        args = self.make_args("start")
        cli_docker_commands.docker_command(args)
        mock_start.assert_called_with(containers=args.containers)

        args = self.make_args("stop")
        cli_docker_commands.docker_command(args)
        mock_stop.assert_called_with(containers=args.containers)

        args = self.make_args("status")
        cli_docker_commands.docker_command(args)
        mock_status.assert_called_with(containers=args.containers)

        args = self.make_args("update", with_image_opts=True)
        cli_docker_commands.docker_command(args)
        mock_update.assert_called_with(
            containers=args.containers,
            defaults=args.defaults,
            image_name=args.image_name,
            image_tag=args.image_tag,
        )

        args = self.make_args("remove")
        cli_docker_commands.docker_command(args)
        mock_remove.assert_called_with(containers=args.containers)

        args = self.make_args("ip")
        cli_docker_commands.docker_command(args)
        mock_ip.assert_called_with(containers=args.containers)

        args = self.make_args("restart")
        cli_docker_commands.docker_command(args)
        mock_restart.assert_called_with(containers=args.containers)

    @mock.patch("tethys_cli.docker_commands.exit")
    @mock.patch("tethys_cli.docker_commands.write_error")
    def test_validate_args_valid_cases(self, mock_write_error, mock_exit):
        args = self.make_args("init", num_containers=1, with_image_opts=True)
        cli_docker_commands.validate_args(args)
        mock_write_error.assert_not_called()
        mock_exit.assert_not_called()

        args = self.make_args("update", num_containers=1, with_image_opts=True)
        cli_docker_commands.validate_args(args)
        mock_write_error.assert_not_called()
        mock_exit.assert_not_called()

        args = self.make_args("init", num_containers=1, with_image_opts=True)
        cli_docker_commands.validate_args(args)
        mock_write_error.assert_not_called()
        mock_exit.assert_not_called()

    @mock.patch("tethys_cli.docker_commands.exit")
    @mock.patch("tethys_cli.docker_commands.write_error")
    def test_validate_args_image_options_multiple_containers(
        self, mock_write_error, mock_exit
    ):
        args = self.make_args("init", num_containers=2, with_image_opts=True)
        cli_docker_commands.validate_args(args)
        mock_write_error.assert_called()
        mock_exit.assert_called()

        args = self.make_args("update", num_containers=2, with_image_opts=True)
        cli_docker_commands.validate_args(args)
        mock_write_error.assert_called()
        mock_exit.assert_called()

    @mock.patch("tethys_cli.docker_commands.exit")
    @mock.patch("tethys_cli.docker_commands.write_warning")
    def test_validate_args_image_options_w_unsupported_command(
        self, mock_write_warning, mock_exit
    ):
        for command in ["start", "stop", "restart", "remove", "ip", "status"]:
            args = self.make_args(command, num_containers=1, with_image_opts=True)
            cli_docker_commands.validate_args(args)
            mock_write_warning.assert_called()
            mock_exit.assert_not_called()

    def test_uih_get_input_with_default(self):
        self.mock_input.side_effect = ["test", ""]

        result = cli_docker_commands.UserInputHelper.get_input_with_default(
            prompt="prompt", default="test_default"
        )
        self.mock_input.assert_called_with("prompt [test_default]:")
        self.assertEqual(result, "test")

        result = cli_docker_commands.UserInputHelper.get_input_with_default(
            prompt="prompt", default="test_default"
        )
        self.mock_input.assert_called_with("prompt [test_default]:")
        self.assertEqual(result, "test_default")

    @mock.patch("tethys_cli.docker_commands.getpass")
    def test_uih_get_verified_password_default(self, mock_getpass):
        mock_getpass.getpass.side_effect = [""]

        passwd = cli_docker_commands.UserInputHelper.get_verified_password(
            prompt="prompt", default="default_pass"
        )
        self.assertEqual(passwd, "default_pass")

        mock_getpass.getpass.assert_called_with("prompt [default_pass]: ")

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.getpass")
    def test_uih_get_verified_password(self, mock_getpass, mock_pretty_output):
        mock_getpass.getpass.side_effect = [
            "pass",
            "foo",
            "pass",
            "pass",
        ]

        passwd = cli_docker_commands.UserInputHelper.get_verified_password(
            prompt="prompt", default="default_pass"
        )
        self.assertEqual(passwd, "pass")

        gp_call_args = mock_getpass.getpass.call_args_list
        self.assertEqual(4, len(gp_call_args))
        self.assertEqual("prompt [default_pass]: ", gp_call_args[0][0][0])
        self.assertEqual("Confirm Password: ", gp_call_args[1][0][0])
        self.assertEqual("prompt [default_pass]: ", gp_call_args[2][0][0])
        self.assertEqual("Confirm Password: ", gp_call_args[3][0][0])

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual(
            "Passwords do not match, please try again.", po_call_args[0][0][0]
        )

    def test_uih_get_valid_numeric_input_default(self):
        self.mock_input.side_effect = [""]

        num = cli_docker_commands.UserInputHelper.get_valid_numeric_input(
            prompt="prompt", min_val=1, max_val=10
        )
        self.assertEqual(num, 1)
        self.mock_input.assert_called_with("prompt (max 10) [1]: ")

    def test_uih_get_valid_numeric_input_valid(self):
        self.mock_input.side_effect = ["5"]

        num = cli_docker_commands.UserInputHelper.get_valid_numeric_input(
            prompt="prompt", min_val=1, max_val=10
        )
        self.assertEqual(num, 5)
        self.mock_input.assert_called_with("prompt (max 10) [1]: ")

    def test_uih_get_valid_numeric_input_invalid(self):
        self.mock_input.side_effect = ["five", "11", "10.0", "10"]

        num = cli_docker_commands.UserInputHelper.get_valid_numeric_input(
            prompt="prompt", min_val=1, max_val=10
        )
        self.assertEqual(num, 10)

        input_call_args = self.mock_input.call_args_list
        self.assertEqual(4, len(input_call_args))
        self.assertEqual("prompt (max 10) [1]: ", input_call_args[0][0][0])
        self.assertEqual(
            "Please enter an integer number\nprompt (max 10) [1]: ",
            input_call_args[1][0][0],
        )
        self.assertEqual(
            "Number must be between 1 and 10\nprompt (max 10) [1]: ",
            input_call_args[2][0][0],
        )
        self.assertEqual(
            "Please enter an integer number\nprompt (max 10) [1]: ",
            input_call_args[1][0][0],
        )

    def test_uih_get_valid_choice_input_default(self):
        self.mock_input.side_effect = [""]

        c = cli_docker_commands.UserInputHelper.get_valid_choice_input(
            prompt="prompt", choices=["a", "b"], default="a"
        )
        self.assertEqual(c, "a")
        self.mock_input.assert_called_with("prompt [A/b]: ")

    def test_uih_get_valid_choice_input_invalid(self):
        self.mock_input.side_effect = [
            "c",
            "d",
            "e",
            "B",
        ]

        c = cli_docker_commands.UserInputHelper.get_valid_choice_input(
            prompt="prompt", choices=["a", "b"], default="a"
        )
        self.assertEqual(c, "b")

        input_call_args = self.mock_input.call_args_list
        self.assertEqual(4, len(input_call_args))
        self.assertEqual("prompt [A/b]: ", input_call_args[0][0][0])
        self.assertEqual(
            "Please provide a valid option\nprompt [A/b]: ", input_call_args[1][0][0]
        )
        self.assertEqual(
            "Please provide a valid option\nprompt [A/b]: ", input_call_args[2][0][0]
        )
        self.assertEqual(
            "Please provide a valid option\nprompt [A/b]: ", input_call_args[3][0][0]
        )

    @mock.patch("tethys_cli.docker_commands.Path.is_dir")
    def test_uih_get_valid_directory_input_default(self, mock_is_dir):
        mock_is_dir.return_value = True
        self.mock_input.side_effect = [""]

        c = cli_docker_commands.UserInputHelper.get_valid_directory_input(
            prompt="prompt", default=gettempdir()
        )
        self.assertEqual(c, gettempdir())
        self.mock_input.assert_called_with(f"prompt [{gettempdir()}]: ")

    @mock.patch("tethys_cli.docker_commands.Path.mkdir")
    @mock.patch("tethys_cli.docker_commands.Path.is_dir")
    def test_uih_get_valid_directory_input_makedirs(self, mock_is_dir, mock_mkdir):
        value = str(Path("/").absolute() / "non" / "existing" / "path")
        self.mock_input.side_effect = [str(Path("non") / "existing" / "path")]
        mock_is_dir.return_value = False

        absolute_return_value = Path("/").absolute() / "non" / "existing" / "path"
        mock_absolute_path = mock.patch(
            "tethys_cli.docker_commands.Path.absolute"
        ).start()
        mock_absolute_path.return_value = absolute_return_value
        c = cli_docker_commands.UserInputHelper.get_valid_directory_input(
            prompt="prompt", default=gettempdir()
        )
        mock.patch.stopall()
        self.assertEqual(c, value)

        self.mock_input.assert_called_with(f"prompt [{gettempdir()}]: ")
        mock_is_dir.assert_called_once()
        mock_mkdir.assert_called_once()

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.Path.mkdir")
    @mock.patch("tethys_cli.docker_commands.Path.is_dir")
    def test_uih_get_valid_directory_input_oserror(
        self, mock_is_dir, mock_mkdir, mock_pretty_output
    ):
        invalid_path = str(Path("/").absolute() / "invalid" / "path")
        valid_path = str(Path("/").absolute() / "foo" / "tmp")
        mock_is_dir.side_effect = [False, True]
        mock_mkdir.side_effect = OSError
        self.mock_input.side_effect = [invalid_path, valid_path]
        c = cli_docker_commands.UserInputHelper.get_valid_directory_input(
            prompt="prompt", default=gettempdir()
        )
        self.assertEqual(c, valid_path)

        mock_pretty_output.assert_called_with(f"OSError(): {invalid_path}")
        input_call_args = self.mock_input.call_args_list
        self.assertEqual(2, len(input_call_args))
        self.assertEqual(f"prompt [{gettempdir()}]: ", input_call_args[0][0][0])
        self.assertEqual(
            f"Please provide a valid directory\nprompt [{gettempdir()}]: ",
            input_call_args[1][0][0],
        )

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.curses")
    @mock.patch("tethys_cli.docker_commands.has_module")
    @pytest.mark.skipif(
        sys.platform == "win32", reason="This test does not run on Windows"
    )
    def test_log_pull_stream_linux_with_id_bad_status(
        self, mock_has_module, mock_curses, mock_pretty_output
    ):
        mock_stream = [
            b'{      "id":"358464",      "status":"foo",      "progress":"bar"   }'
        ]
        mock_has_module.return_value = True
        mock_curses.initscr().getmaxyx.return_value = 1, 80

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_any_call(
            0,
            0,
            "foo                                                   "
            "                         ",
        )
        mock_curses.initscr().addstr.assert_called_with(
            1,
            0,
            "---                                                 "
            "                           ",
        )
        mock_curses.initscr().refresh.assert_called_once()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual("", po_call_args[0][0][0])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.curses")
    @mock.patch("tethys_cli.docker_commands.has_module")
    @pytest.mark.skipif(
        sys.platform == "win32", reason="This test does not run on Windows"
    )
    def test_log_pull_stream_linux_with_id_progress_status(
        self, mock_has_module, mock_curses, mock_pretty_output
    ):
        mock_stream = [
            b'{      "id":"358464",      "status":"Downloading",      "progress":"bar"   }'
        ]
        mock_has_module.return_value = True
        mock_curses.initscr().getmaxyx.return_value = 1, 80

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_called_with(
            0,
            0,
            "358464: Downloading bar                             "
            "                           ",
        )
        mock_curses.initscr().refresh.assert_called_once()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual("", po_call_args[0][0][0])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.curses")
    @mock.patch("tethys_cli.docker_commands.has_module")
    @pytest.mark.skipif(
        sys.platform == "win32", reason="This test does not run on Windows"
    )
    def test_log_pull_stream_linux_with_id_status(
        self, mock_has_module, mock_curses, mock_pretty_output
    ):
        mock_stream = [
            b'{      "id":"358464",      "status":"Downloading",      "progress":"bar"   }\r\n'
            b'{      "id":"358464",      "status":"Pulling fs layer",      "progress":"baz"   }'
        ]
        mock_has_module.return_value = True
        mock_curses.initscr().getmaxyx.return_value = 1, 80

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_called_with(
            0,
            0,
            "358464: Downloading bar                             "
            "                           ",
        )
        mock_curses.initscr().refresh.assert_called()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual("", po_call_args[0][0][0])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.curses")
    @mock.patch("tethys_cli.docker_commands.has_module")
    @pytest.mark.skipif(
        sys.platform == "win32", reason="This test does not run on Windows"
    )
    def test_log_pull_stream_linux_with_no_id(
        self, mock_has_module, mock_curses, mock_pretty_output
    ):
        mock_stream = [b'{      "status":"foo",      "progress":"bar"   }']
        mock_has_module.return_value = True
        mock_curses.initscr().getmaxyx.return_value = 1, 80

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_not_called()
        mock_curses.initscr().refresh.assert_not_called()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual("foo", po_call_args[0][0][0])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.curses")
    @mock.patch("tethys_cli.docker_commands.has_module")
    @pytest.mark.skipif(
        sys.platform == "win32", reason="This test does not run on Windows"
    )
    def test_log_pull_stream_linux_with_curses_error(
        self, mock_has_module, mock_curses, mock_pretty_output
    ):
        import curses

        mock_stream = [
            b'{      "id":"358464",      "status":"Downloading",      "progress":"bar"   }\r\n'
        ]
        mock_has_module.return_value = True
        mock_curses.initscr().getmaxyx.return_value = 1, 80
        mock_curses.error = (
            curses.error
        )  # Since curses is mocked, need to reinstate this as a curses error
        mock_curses.initscr().addstr.side_effect = curses.error  # Raise Curses Error

        cli_docker_commands.log_pull_stream(mock_stream)

        mock_curses.initscr().addstr.assert_called_with(
            0,
            0,
            "358464: Downloading bar                             "
            "                           ",
        )
        mock_curses.initscr().refresh.assert_called_once()
        mock_curses.noecho.assert_called_once()
        mock_curses.cbreak.assert_called_once()
        mock_curses.echo.assert_called_once()
        mock_curses.nocbreak.assert_called_once()
        mock_curses.endwin.assert_called_once()

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual("", po_call_args[0][0][0])

    @mock.patch("tethys_cli.docker_commands.write_pretty_output")
    @mock.patch("tethys_cli.docker_commands.has_module")
    def test_log_pull_stream_windows(self, mock_has_module, mock_pretty_output):
        mock_stream = [
            b'{      "id":"358464",      "status":"Downloading",      "progress":"bar"   }'
        ]
        mock_has_module.return_value = False

        cli_docker_commands.log_pull_stream(mock_stream)

        po_call_args = mock_pretty_output.call_args_list
        self.assertEqual(1, len(po_call_args))
        self.assertEqual("358464:Downloading bar", po_call_args[0][0][0])

    @mock.patch("tethys_cli.docker_commands.exit")
    @mock.patch("tethys_cli.docker_commands.write_error")
    @mock.patch(
        "tethys_cli.docker_commands.docker.from_env",
        side_effect=cli_docker_commands.docker.errors.DockerException,
    )
    def test_docker_deamon_not_running(self, _, mock_write_error, mock_exit):
        cli_docker_commands.ContainerMetadata._docker_client = None
        cli_docker_commands.ContainerMetadata.get_docker_client()
        mock_write_error.assert_called()
        mock_exit.assert_called_with(1)
