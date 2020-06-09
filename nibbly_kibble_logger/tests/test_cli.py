"""Test of the command-line interface"""
import os
import pytest

from click.testing import CliRunner

from nibbly_kibble_logger import app


class TestForgottenLogPath:

    @pytest.fixture(scope='class')
    def invocation(self):
        return CliRunner().invoke(app.cli, ['run'])

    def test_nonzero_return_code(self, invocation):
        assert invocation.exit_code != 0

    def test_useful_error_message(self, invocation):
        assert 'Missing command' in invocation.output


class TestLogPathHandling:

    def test_log_file_need_not_exist(self, tmpdir):

        filename = str(tmpdir.join('my_awesome_log.log'))

        context = app.cli.make_context('nibbly_kibble_logger', [filename, 'run'])
        assert context.params['record_filename'] == filename

    def test_log_file_is_absolute_path(self):

        filename = 'my_awesome_log.log'

        context = app.cli.make_context('nibbly_kibble_logger', [filename, 'run'])
        assert context.params['record_filename'] == os.path.abspath(filename)

    def test_log_file_must_be_writable(self, monkeypatch):

        # This is inherently fragile to click changing how it checks for writability.
        # For example, I consider it to be a bug that it assumes that all files that do not exist
        # are writable.

        def fake_access(path, mode, *args, **kwargs):
            return False

        monkeypatch.setattr(os, 'access', fake_access)

        invocation = CliRunner().invoke(app.cli,
                                        [os.path.abspath(__file__),  # the one file I know exists
                                         'run'])

        assert invocation.exit_code != 0 and 'writable' in invocation.output.lower()

    @pytest.mark.xfail(reason="click really does expanduser, but I guess not when calling through "
                              "a CliRunner?")
    def test_log_file_can_use_tilde(self, monkeypatch):

        filename = '~/my_awesome_log.log'

        script_infos = []

        def fake_create_app(script_info):
            script_infos.append(script_info)

        monkeypatch.setattr(app, 'create_app', fake_create_app)

        invocation = CliRunner().invoke(app.cli, [filename,  'run'])
        assert invocation.exit_code == 0

        assert len(script_infos) == 1
        assert script_infos[0].record_filename == os.path.expanduser(filename)






