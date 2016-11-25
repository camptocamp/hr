FROM camptocamp/odoo-project:9.0-1.7.1
MAINTAINER Camptocamp

# Install additional debian packages if needed
# RUN set -x; \
#         apt-get update \
#         && apt-get install -y --no-install-recommends \
#         python-shapely \
#         && apt-get clean \
#         && rm -rf /var/lib/apt/lists/*

# Install additional python packages if needed
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

ENV ADDONS_PATH="/opt/odoo/external-src/enterprise, \
  /opt/odoo/src/addons, \
  /opt/odoo/external-src/server-tools, \
  /opt/odoo/external-src/product-variant, \
  /opt/odoo/external-src/web, \
  /opt/odoo/external-src/connector, \
  /opt/odoo/external-src/hr-timesheet, \
  /opt/odoo/external-src/hr, \
  /opt/odoo/local-src," \
  LIMIT_TIME_CPU=86400 \
  LIMIT_TIME_REAL=86400 \
  LIMIT_MEMORY_SOFT=1342177280 \
  LIMIT_MEMORY_HARD=1610612736
