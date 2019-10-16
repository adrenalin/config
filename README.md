[![Build Status](https://travis-ci.com/Houston-Analytics/ais-api.svg?token=A3Jf8xqAeS2y2pmpzUs8&branch=master)](https://travis-ci.com/Houston-Analytics/ais-api)

# 1 Installation and dependencies

Install dependencies

```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Install or configure Redis for cache engine if your system is configured to
use Redis.


# 2 Configuration

There are three levels that can be used to override configuration settings:

1. [local configuration file](#local-configuration-files)
2. [environment variables](#environment-variables)
3. [AWS SecretsManager](#aws-secretsmanager)

## <a name="local-configuration-files"></a> 2.1 Local configuration file

It is possible to override database string in file `./config/local.yml`. Local
configuration options override per key the ones defined in `./config/defaults.yml`
which are used when there are no overrides.

```
db:
  name: 'aistest'
  username: 'ais_database_admin_username'
  password: 'ais_database_admin_password'
```

## <a name="environment-variables"></a> 2.2 Environment variables

It is possible override any default and local configuration by using environment
variables. Environment variables follow the same naming scheme as configuration
paths, but in uppercase and separated by underscore (`_`).

E.g. configuration path `db.username` can be overridden with `DB_USERNAME` and
correspondingly `server.session.engine` with `SERVER_SESSION_ENGINE`.

If `DB_CONNECTION_STRING` is present it is used fully. Otherwise a combination of
`DB_USERNAME`, `DB_PASSWORD`, `DB_HOST` and `DB_NAME` will be used.

Environment variables are used on the command line in the following manner:

```
DB_USERNAME=aistest DB_PASSWORD=randompassword DB_NAME=ais pytest
DB_CONNECTION_STRING=postgresql:///aistest alembic upgrade base
```

Environment variables are especially for production use, for development it is
recommended to create a local configuration file as described above.

There are three case insensitive magic environment variables that are typecasted:

- `false` is casted `False`
- `true` is casted as `True`
- `null` and `none` are casted as `None`

This leads into easier true/false evaluations in the code. For example this will
disable AWS SecretsManager when running the application:

`AWS_SECRETSMANAGER_ENABLED=false python3 application.py`

## <a name="aws-secretsmanager"></a> 2.3 AWS SecretsManager

The final layer of configurability is on
[AWS SecretsManager](https://eu-north-1.console.aws.amazon.com/secretsmanager/home?region=eu-north-1).

### 2.3.1 Normal values

Each configuration key can be overridden by the string representation of the
configuration path. E.g. configuration option

```
db:
  connection_string: 'postgresql://postgres@localhost/ais'
```

can be overridden with AWS SecretsManager secret key `db.connection_string`


### 2.3.2 Namespaced values

Since it is expected that as the system grows there might be conflicts in the
naming. It is possible to use namespaced strings to avoid inter application
conflicts. Namespace is defined in `aws.secretsmanager.prefix`, which is
prepended to the configuration key read from AWS SecretsManager, i.e.
system with secretsmanager prefix `ais.dev` will read `ais-dev.db.connection_string`
as `db.connection_string` and skip any secret that does not contain the prefix.


# 3 Alembic database migrations

Quickstart guide to [Alembic](https://alembic.sqlalchemy.org/):

1. Migrate to the latest revision

```
alembic upgrade head
```

2. Downgrade to a specific revision

```
alembic downgrade $revision
```

3. Revert back to the initial state with a blank schema. WARNING! This will delete all data!

```
alembic downgrade base
```

4. Create a new migration

```
alembic revision -m 'Revision description here'
```


# 4 Running tests

Run all the tests with [pytest](https://pytest.org)

```
pytest
```

# 5 pylint

Pylint was chosen as nearly default given by v2.3.1, disabling only a few
modules:

- `duplicate-code`
  - this is disabled, since Alembic definitions and unit tests include a lot of
    repetition
- `wrong-import-order`
  - all Alembic migrations have wrong import order by default
- `too-few-public-methods`
  - routers and tests have often especially in the beginning one method only


# 6 Running the application

Use this command to run the application from command line

```
python application.py
```

Routers are defined in `./routers` and they extend the abstract class `Router`
located in `./lib/router.py`.


## 6.1 graphical user interface

To extend the API with graphical user interface please clone the repository
[git@github.com:Houston-Analytics/ais-gui.git](https://github.com/Houston-Analytics/ais-gui)
and build it according to the instructions (`npm run build` in short).

When the build is ready, remove the placeholder directory `./client` and create
a symbolic link to the build directory in its place.


## 7 GUI configuration

The configuration domain for the graphical user interface is `react`.


### 7.1 Configuring space planner

Space planner editor is built fully according to the configuration. The only
default field is `assortment` which is defined in `config/defaults.yml` and the
rest are to be defined per customer.

Structure of each of the elements is the following:

- storage key or the key of the value that will be stored in the `parameters`
  of the scenario
  - widget
    - currently supported: `buttons`, `select`, `grid`, `number`
  - grouping (optional)
    - grouping creates a visual structure
      - each group acts as an id, which is localized and displayed as the
        group title
  - options
    - an array of dictionary objects that define at least `value` which is used
      as the storage value and optionally `label` which is the human readable
      value
      - if a label is not defined the value will be used instead
      - human readable value is passed through localization
  - default
    - optional default value for the field


#### 7.1.1 buttons widget

Buttons widget displays a horizontal group of buttons of which only one can be
selected at each time


#### 7.1.2 grid widget

Grid widget creates a button grid. An extra numeric option `size` is required
and it defines how many rows are displayed. Storage key will be appended by
the index, so `size: 4` will create storage keys `{storage_key}_1`,
`{storage_key}_2`, `{storage_key}_3` and `{storage_key}_4`.


#### 7.1.3 number widget

Number widget creates a numeric input. The extra options are mainly defined by
HTML5 `<input type="number" />` DOM element. Any of the following options is
optional:

- `min` defines the minimum value
- `max` defines the maximum value
- `default` defines the default value
- `step` defines the discreet step size or precision of the value
  - i.e. with `step: 0.01` it is possible to set values
    0, 0.01, 0.02, 0.03, ...
- `unit` is to display an optional unit in the label; unit will be localized


#### 7.1.4 Configuration example

An example configuration:

```
react:
  space_planning:
    blocking_criteria:
      widget: 'buttons'
      grouping: 'blocking_criteria'
      options:
        - value: 'brand_id'
          label: 'brand'
        - value: 'category_level_3'
          label: 'Category level 3'
    product_order_criteria:
      widget: 'grid'
      size: 4
      grouping: 'product_order_criteria'
      options:
        - value: 'brand_id'
          label: 'brand'
        - value: 'category_level_3'
          label: 'Category level 3'
        - value: 'height'
        - value: 'price'
        - value: 'unit_margin'
        - value: 'lifestyle_number'
        - value: 'size'
        - value: 'quality'
    up_down_order_criteria:
      widget: 'buttons'
      grouping: 'up_down_order_criteria'
      options:
        - value: 'weight'
        - value: 'price'
    shortage_penalty:
      widget: 'number'
      grouping: 'optimization_parameters'
      min: 0
      default: 10
    shelf_up_down_penalty:
      widget: 'number'
      grouping: 'optimization_parameters'
      min: 0
      default: 0.1
      step: 0.1
    count_products_on_store:
      widget: 'number'
      grouping: 'optimization_parameters'
      min: 0
      default: 100
      step: 1
      disabled: true
    block_dislocation_penalty:
      widget: 'number'
      grouping: 'optimization_parameters'
      default: 0.01
      step: 0.01
      disabled: true
    empty_space_penalty:
      widget: 'number'
      grouping: 'optimization_parameters'
      default: 0.5
      step: 0.1
    time_limit:
      widget: 'number'
      grouping: 'optimization_parameters'
      min: 1
      default: 60
      unit: 'seconds'
    first_time_limit:
      widget: 'number'
      grouping: 'optimization_parameters'
      min: 1
      default: 30
      unit: 'seconds'

```
