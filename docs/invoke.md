# Using automated tasks with Invoke

This project uses `invoke` to run some automated tasks.

First, install it with:

```bash

$ sudo pip install invoke

```

You can now see the list of tasks by running at the root directory:

```bash

$ invoke --list

```

The tasks are defined in `tasks.py`.

## Some tasks

### release.bump

release.bump is used to bump the current version number:
(see [releases.md](docs/releases.md#versioning-pattern) for more informations about versionning)

```
invoke release.bump --feature
# or
invoke release.bump --patch
```

--feature will change the minor version number (eg. 9.1.0 to 9.2.0).
--patch will change the patch version number (eg 9.1.0 to 9.1.1).

bump.release changes following files (which must be commited):
 * [odoo/VERSION](../odoo/VERSION): just contains the project version number, so this version is changed.
 * [HISTORY.rst](../HISTORY.rst): Rename Unreleased section with the new version number and create a new unreleased section.
 * rancher/integration/docker-compose.yml: Change the version of the docker image to use for the integration stack.


