# `nibbly_kibble_logger`

Logger for the Nibbly Kibble Raceway

## About the Nibbly Kibble Raceway
The Nibbly Kibble Raceway is a a 180-stud-long two-lane Lego car drag strip, with an
electronically-controlled timing system inspired by and reverse engineered from the
[circa-2018](https://www.youtube.com/watch?v=ZsoP0Kqq-NI)
system used by [3DBotMaker](https://www.3dbotmaker.com/)
on [Race Mountain Speedway](https://www.youtube.com/channel/UCjN5K3IYZgz-vCWhI_DD01A)
(I didn't come across
[this circuit diagram](https://www.3dbotmaker.com/forum/main/comment/5e0680731671060017170f59)
until after I'd already built my system, which is a shame, because it would have saved me
_so_ much trial and error).

## Race Logging
Recording race times is a little bit silly, as any races I care about logging
are going to be captured in video, and any conceivable system I set up can't
possibly automatically capture the complete metadata I'd actually want to log
(read: competitors and winners), but what the heck! It's a fun project.

With the
[actual timing system](https://github.com/OpenBagTwo/NibblyKibbleTimingSystem)
running on a Wi-Fi enabled microcontroller, the idea is for each race time to be
POSTed to a REST API which then writes that time to file, along with the date
and time of the race.

This logger runs as a simple Flask app. **Disclaimer:** This application is
quick, dirty and horribly insecure. If someone managed to get ahold of your
IP and had access to the port running Flask, they could just spam POST requests,
DDoSing you, filling up your hard drive, or who knows what else. I
**absolutely** do not recommend running this continuously or starting it on
boot.

## Installation

To install this application, clone the repo, create a virtual environment
based around Python 3 and, from the project root and your virtual environment,
run
```bash
$ pip install -e .
```

I'm sure you can also install
[straight from github](https://adamj.eu/tech/2019/03/11/pip-install-from-a-git-repository/).

### Development
If you want to develop this code, go nuts! I recommend using
[conda](https://docs.conda.io/en/latest/index.html) and using the
[environment.yml](environment.yml) file contained in this repo
to get started: clone the repo, navigate to the folder root and run:
```bash
$ conda env create
```

### Testing
You can make sure this package is working by running its test suite using
[`py.test`](https://docs.pytest.org/en/stable/). After installing `pytest` (and
`pytest-cov` if you'd like) via `pip` or `conda`, navigate to the project
root and run:
```bash
$ py.test
```

## How To Use

The syntax to run the logger server is:

```bash
$ nibbly_kibble_logger RECORD_FILE run [--port PORT]
```

where `RECORD_FILE` is the path (relative or absolute) to the file you want to
use for race logging. If the file already exists, it will be appended, but if
you specify a filename in a directory which does not exist, you'll get an error.

### Logging API
The logger server accepts POST requests to the `api/record` end-point. The
posted data can either be plain text (should just be the drag time) or JSON,
which can contain additional metadta.

### Example Usage

1. Start the server:
```bash
$ nibbly_kibble_logger ~/Desktop/racetimes.log run --port 7654
```

2. In a new terminal, post data using [curl](https://curl.haxx.se/)
```bash
$ curl -d '6.23' -H "Content-Type: text/plain" -X POST http://localhost:7654/api/record
$ curl -d '{"drag_time":"5.95", "lane 1":"mustang", "lane 2":"camaro", "winning lane":"2", "loser status":"finish"}' -H "Content-Type: application/json" -X POST http://localhost:7654/api/record
```

3. Kill the server using Ctrl-C! This flask app is horribly insecure. Do not
leave it running!

3. View your logs:
```bash
$ cat ~/Desktop/racetimes.log
{"drag time": 6.23, "timestamp": "2020-06-08 21:49:40"}
{"drag_time": "5.95", "lane 1": "mustang", "lane 2": "camaro", "winning lane": "2", "loser status": "finish", "timestamp": "2020-06-08 21:49:44"}
```
