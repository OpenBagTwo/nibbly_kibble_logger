"""Flask app serving up a REST interface for logging"""
import datetime as dt
import json
from os import path

import click
from flask import abort, Flask, request
from flask.cli import FlaskGroup, pass_script_info


def create_app(script_info):
    """Set up Flask app for logging

    Args:
        script_info (flask.cli.ScriptInfo): Configuration passed in from the command line.
            Contains `script_info.record_filename`, the filename to be used to record race data.
    Returns:
        flask.app.Flask: the properly configured Flask app

    """
    app = Flask(__name__)
    app.config['RECORD_FILE'] = script_info.record_filename

    @app.route('/api/record', methods=['POST'])
    def record_race():
        """Write POSTed race data to file. The POSTed data can either be:

        - plaintext, in which case it is assumed that the data is just the race time
        - JSON, which should contain additional metadata about the competitors (and winner?)

        Note:
            I shudder to think how this would function in a multithreaded setting.

        """
        timestamp = dt.datetime.now().strftime('%Y-%M-%D %H:%m:%S')
        try:
            if request.headers['Content-Type'] == 'text/plain':

                record = {'drag time': float(request.data)}
            elif request.headers['Content-Type'] == 'application/json':
                record = request.get_json()
            else:
                abort(400)
        except:  # noqa
            abort(400)

        record['timestamp'] = timestamp

        with open(app.config['RECORD_FILE'], 'a') as record_file:
            json.dump(record, record_file)
            record_file.write('\n')
            record_file.flush()
        return 'OK'

    return app


@click.argument('record_filename', type=click.Path(dir_okay=False, writable=True, resolve_path=True))
@click.group(cls=FlaskGroup, create_app=create_app)
@pass_script_info
def cli(script_info, record_filename):
    """Command-line entry-point for `nibbly_kibble_logger`

    Args:
        record_filename (str): Path to the file to be used for logging. If the file already exists,
            it will be appended.
    """
    if not path.exists(path.dirname(record_filename)):
        raise FileNotFoundError('The specified log path points to a directory which does not exist '
                                'or to which you cannot write.')
    script_info.record_filename = record_filename



