FROM registry.gitlab.com/hibou-io/hibou-odoo/suite-enterprise:13.0-test

COPY --chown=104 ./ /opt/odoo/addons
COPY ./odoo.conf.sample /etc/odoo/odoo.conf

