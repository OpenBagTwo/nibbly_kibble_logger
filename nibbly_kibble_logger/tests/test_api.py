"""Test of the Nibbly Kibble Logger REST API"""
import datetime as dt
import json
import pytest

from unittest.mock import MagicMock

from flask.cli import ScriptInfo
from nibbly_kibble_logger.app import create_app


@pytest.fixture
def record_filename(tmpdir):
    return str(tmpdir.join('my_awesome_log.log'))


@pytest.fixture
def app(record_filename):
    script_info = ScriptInfo(create_app=create_app)
    script_info.record_filename = record_filename

    return create_app(script_info)


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


class TestPost:

    def test_post_plaintext(self, client, record_filename):
        resp = client.post('/api/record', data='3.14', content_type='text/plain')
        assert resp.status == '200 OK'

        recorded_data = open(record_filename).readlines()
        assert len(recorded_data) == 1
        assert json.loads(recorded_data[0])['drag time'] == 3.14

    def test_post_bad_plaintext(self, client):
        resp = client.post('/api/record', data="three years", content_type='text/plain')
        assert resp.status == '400 BAD REQUEST'

    def test_post_json(self, client, record_filename):
        resp = client.post('/api/record', json={'drag time': 4.52,
                                                'lane 1': 'twin mill',
                                                'lane 2': 'bone shaker',
                                                'winning lane': 1,
                                                'loser status': 'dnf'})
        assert resp.status == '200 OK'
        recorded_data = open(record_filename).readlines()
        assert len(recorded_data) == 1
        assert json.loads(recorded_data[0])['drag time'] == 4.52

    def test_post_invalid_content_type(self, client):
        resp = client.post('/api/record', data={'drag time': 4.52,
                                                'lane 1': 'twin mill',
                                                'lane 2': 'bone shaker',
                                                'winning lane': 1,
                                                'loser status': 'dnf'})
        assert resp.status == '400 BAD REQUEST'

    def test_post_appends_to_existing_file(self, client, record_filename):
        with open(record_filename, 'w') as f:
            f.write('messing up your logs\n')

        resp = client.post('/api/record', data='3.14', content_type='text/plain')
        assert resp.status == '200 OK'

        recorded_data = open(record_filename).readlines()
        assert len(recorded_data) == 2
        assert json.loads(recorded_data[1])['drag time'] == 3.14
        assert recorded_data[0] == 'messing up your logs\n'

    def test_timestamping(self, client, record_filename, monkeypatch):
        # solution adapted from https://stackoverflow.com/a/60629703
        datetime_mock = MagicMock(wraps=dt.datetime)
        datetime_mock.now.return_value = dt.datetime(2020, 6, 8, 22, 30, 18)
        monkeypatch.setattr(dt, "datetime", datetime_mock)

        resp = client.post('/api/record', data='3.14', content_type='text/plain')
        assert resp.status == '200 OK'

        recorded_data = open(record_filename).readlines()
        assert len(recorded_data) == 1
        assert json.loads(recorded_data[0]) == {'drag time': 3.14,
                                                'timestamp': '2020-06-08 22:30:17'}
