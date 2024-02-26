#!/bin/bash

# pg_restore -U postgres --dbname=acts_ph4 -n ntg --verbose --single-transaction < backup/acts_ph4.dump
# pg_restore -U postgres --dbname=mark_ph35 -n ntg --verbose --single-transaction < backup/mark_ph35.dump
pg_restore -U postgres --dbname=gal_ph1 -n ntg --verbose --single-transaction < backup/gal_ph1_mon.dump
pg_restore -U postgres --dbname=eph_ph1 -n ntg --verbose --single-transaction < backup/eph_ph1_mon.dump