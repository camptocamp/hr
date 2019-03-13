FROM camptocamp/odoo-project:10.0-3.1.0
MAINTAINER Camptocamp

# Steps are grouped by dependency
# and ordered by compromizing cost and frequency

## Base requirements (Libs and packages)
# frequency: rarely
# cost:      high

COPY ./*requirements.txt /odoo/

# Install additional debian packages
RUN set -x; \
        apt-get update \
        && apt-get install -y --force-yes --no-install-recommends \
        python-dev \
        build-essential \
        libffi-dev \
        libssl-dev \
        cups \
        libcups2-dev \
        git \
        && curl -o wkhtmltox.deb -SL https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.jessie_amd64.deb \
        && echo '4d104ff338dc2d2083457b3b1e9baab8ddf14202 wkhtmltox.deb' | sha1sum -c - \
        && dpkg --force-depends -i wkhtmltox.deb \
        && apt-get -y install -f --no-install-recommends \
        && cd /odoo && pip install -r requirements.txt \
        # Install additional python packages
        && apt-get remove -y python-dev build-essential libffi-dev libssl-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

## Tools of odoo-template
# frequency: seldom
# cost:      light

# Entrypoints
COPY ./before-migrate-entrypoint.d/* /before-migrate-entrypoint.d/
COPY ./start-entrypoint.d/* /start-entrypoint.d/
RUN chmod +x /before-migrate-entrypoint.d/* \
    && chmod +x /start-entrypoint.d/*
# CSV Loader
# `parallel` + `importer.sh` are needed to load heavy files
COPY ./bin/importer.sh /odoo-bin/

## Prepare pip install
# frequency: never
# cost     : very light
COPY ./setup.py /odoo/

## Main activity
# frequency: always
# costs:     very high to very light
COPY ./src /odoo/src
COPY ./external-src /odoo/external-src
COPY ./local-src /odoo/local-src
COPY ./data /odoo/data
COPY ./songs /odoo/songs
COPY ./VERSION /odoo/
COPY ./migration.yml /odoo/

# depends on ./setup.py ./src, ./songs and ./VERSION
RUN cd /odoo && pip install -r src_requirements.txt


## PLATFORM: Add this line to ADDONS_PATH if hosting is on cloud platform
# /odoo/external-src/odoo-cloud-platform, \

## Environment
# frequency: sometimes
# cost:      very light
ENV ADDONS_PATH="/odoo/external-src/enterprise, \
  /odoo/src/addons, \
  /odoo/external-src/account-analytic, \
  /odoo/external-src/account-financial-tools, \
  /odoo/external-src/account-financial-reporting, \
  /odoo/external-src/account-invoicing, \
  /odoo/external-src/connector, \
  /odoo/external-src/connector-exchange, \
  /odoo/external-src/connector-telephony, \
  /odoo/external-src/connector-jira, \
  /odoo/external-src/currency, \
  /odoo/external-src/hr, \
  /odoo/external-src/hr-timesheet, \
  /odoo/external-src/margin-analysis, \
  /odoo/external-src/mis-builder, \
  /odoo/external-src/partner-contact, \
  /odoo/external-src/product-variant, \
  /odoo/external-src/purchase-workflow, \
  /odoo/external-src/report-print-send, \
  /odoo/external-src/sale-workflow, \
  /odoo/external-src/server-tools, \
  /odoo/external-src/queue, \
  /odoo/external-src/project, \
  /odoo/external-src/web, \
  /odoo/external-src/reporting-engine, \
  /odoo/external-src/odoo-cloud-platform, \
  /odoo/external-src/odoo-enterprise-addons, \
  /odoo/external-src/odoo-usability, \
  /odoo/external-src/social, \
  /odoo/external-src/account-closing, \
  /odoo/external-src/bank-payment, \
  /odoo/external-src/l10n-france, \
  /odoo/external-src/intrastat, \
  /odoo/local-src" \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736 \
  ODOO_DATA_PATH=/odoo/data
