# apppack-template


Bare example of a Django project ready to be deployed on AppPack. Start new projects using this repo as a template. Once you've created your project from this template, you should be able to deploy it immediately and verify that it's wired up correctly - the homepage verifies that your database, Redis cache, S3 file storage, and email are all set up and working.

This repo can be used in one of two ways:

1) Create your new repo using this repo as a template, deploy it via AppPack, verify that services are working, then modify as needed.

2) To convert an existing ES web app to an AppPack deployment, note the unique aspects of this repo and make sure they are represented in your project.

See the [ES AppPack documentation](https://energy-solution.atlassian.net/wiki/spaces/ISO/pages/1103266064/Using%2BAppPack), as well as AppPack's [official documentation](https://docs.apppack.io/how-to/apps/).

### Plumbing check:

![Plumbing screenshot](poynter/static/img/plumbing.jpg?raw=true "Plumbing screenshot")

## Localhost installation

Pre-requisites: Ensure you have these installed globally:

- python 3.12.x
- postsgres
- redis (optional)

**When creating your new project repo in github, select the Repository Template option and choose `apppack-template` as the template.**

Assuming your project is called `some_proj`, do:

```
createdb some_proj
cd ~/dev
git clone git@github.com:energy-solution/some_proj.git
cd some_proj
make dev_refresh   # Initializes the virtual environment and installs dependencies
source .venv/bin/activate  # Activates the environment
manage.py migrate

# If not using redis, set up db caching
manage.py createcachetable
```

### Local settings

We do not use the standard `local.py` system for local secrets management. Instead, we use
Lincoln Loop's [goodconf](https://github.com/lincolnloop/goodconf), which is both
[12-Factor](https://12factor.net)-compliant and can be used to "hoist" environment variables into
Django project settings.

To generate a local .yml file storing your local secrets, copy `poynter/config/local.example.yml`
to `poynter/config/local.yml` and edit its vars `local.yml` to match your system.
You can give this file a different name once you've got things up and running, then modify the
reference to it in `config.py`.

Goodconf lets you defined this file either as .yml or .json, but we recommend .yml because
it lets you store comments.

## Caching

This project is set up to run with either a Redis cache or Django database caching. Caching is part
of the demo site, but Redis is not enabled by default in order to avoid an "expensive" service being
left on when not needed.

If you do nothing, you'll get datbase caching, which is fine for light caching needs.

If you want Redis, be sure to select it during app creation, and set the environment variable
`REDIS_ENABLED=True`. Notice that this var is set to a default of `False` in `config.py`.
Note the conditional caching in `settings.py`.

If you want to use database-level caching, run (just once):

`manage.py createcachetable`

## File storage (S3)

AppPack projects are stateless and must not store important files on the current server instance.
Use `default_storage` for all file operations - this guarantees that files are stored in the right
place whether you're on localhost (MEDIA_ROOT) or a server (S3). If you use `model.FileField`, this
abstraction will be handled automatically.

References files in templates as shown in this project's `home.html`, i.e.
`{{ record.attachment.url }}`

If not using FileField, the abstraction should always be handled with Django's `default_storage`:

```
from django.core.files.storage import default_storage

rawfile = open("path/to/data", rb)
new_stored_file = default_storage.save(name="desired/named/file.foo", content=rawfile)
file_url = default_storage.url(new_stored_file)
```

Alternatively, you can use Django's ContentFile to work with raw data that has not been stored on disk:

```
from django.core.files.base import ContentFile

stored_file = default_storage.save(name="whatever", content=ContentFile(raw_data))
```

## Email Test

AWS servers can send email through SES without needing to configure SMTP settings.
For this to work, your project must be configured to send email from the current
AppPack server instance (most ES projects only send live email from the production instance).

For your demo site to be able to send live email you'll need to set two environment variables:

```
apppack -a ap-prod config set ENVIRONMENT=production
apppack -a ap-prod config set TEST_EMAIL_TO=[you]@energy-solution.com
```

Try clicking the Send Mail button both before and after setting these env vars
(wait a few minutes after setting them before trying again).

## Users export for SOC audits

All ES web apps must provide a list of active users in a report for SOC admins every quarter.
An Admin Action on the Users model is provided for this purpose, with Admin filters.
Select Users and then Export CSV.

### Changing Python Dependencies

To add, remove, or change the project's Python dependencies, edit `base.in` (global) or `dev.in`
(developer only). To "lock" your dependencies, run `make requirements.txt` or `make
requirements/dev.txt` or both. Because make is smart about these things, it will only do something
if the source files (base.in or dev.in) have changed. Note that this also means that updates to
the unversioned packages referenced in dev.in won't be picked up automatically! You can force
it to upgrade them with:

```
pip-compile --generate-hashes --output-file=requirements.txt requirements/base.in
pip-compile --generate-hashes --output-file=requirements/dev.txt requirements/dev.in
```

or, to just force it to update one package, do:

```
pip-compile --generate-hashes --output-file=requirements.txt -P dj-database-url requirements/base.in

pip-compile --generate-hashes --output-file=requirements/dev.txt -P pip-tools requirements/dev.in
```

(specify `-P <package_name>`)

n.b. Technically, the Makefile is optional - it's just a convenience wrapper around `pip-compile`.

## AppPack notes

See the ES documentation on AppPack [here](https://energy-solution.atlassian.net/wiki/spaces/ISO/pages/1103266064/AppPack+for+Developers)

## Enable BasicAuth

All non-production server instances should have BasicAuth enabled, to keep out
the googlebot and looky-loos. Run this command for all non-prod instances:

`apppack -a [yourserver/pipeline] config set WSGI_AUTH_CREDENTIALS=esn:solutions`

