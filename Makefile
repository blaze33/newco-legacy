##! make
# A Makefile to automate things
SHELL := /bin/bash

all:

clean:
	find . -name "*.pyc" -delete
	find . -name "*~" -delete

BRANCH = $(shell cat .hg/branch)
REMOTE_URL = $(shell git config --get remote.$(BRANCH).url)
APP = $(shell echo $(REMOTE_URL)|cut -d":" -f2|cut -d"." -f1)
DATE = $(shell date --rfc-3339=date)
PGDUMPURL = $(shell heroku pgbackups:url --app newco-prod)

SYNCDB = django-admin.py syncdb --noinput
MIGRATE = django-admin.py migrate
COLLECTSTATIC = django-admin.py collectstatic --noinput
SQLDIFFALL = django-admin.py sqldiffall --settings=newco.settings.dev

define SYNC_CMD
$(SYNCDB) && \
$(MIGRATE)
endef

echo: clean
	@echo $(BRANCH) $(REMOTE_URL) $(APP) $(DATE) $(PGDUMPURL)

maintain_on:
	heroku maintenance:on --app $(APP)

maintain_off:
	heroku maintenance:off --app $(APP)


push:
	hg bookmark -f -r $(BRANCH) master
	hg --verbose push git+ssh://$(REMOTE_URL)

sync:
	heroku run '$(SYNC_CMD)' --app $(APP)

sqldiffall:
	heroku run '$(SQLDIFFALL)' --app $(APP)

collectstatic:
	heroku run '$(COLLECTSTATIC)' --app $(APP)

heroku_bash:
	heroku run bash --app $(APP)

simple_deploy:
	@echo 'Check for uncommited changes:'
	hg summary | grep -q 'commit: (clean)'
	@echo 'Check for unapplied migrations:'
	# TODO: need to check against remote db...
	python newco/apps/utils/scripts/new-migrations.py
	hg up -C staging
	hg merge -r default
	hg commit -m "Merge with default"
	make push
	hg up -C production
	hg merge -r staging
	hg commit -m "Merge with staging"
	make push

pg_backup2dropbox:
	curl -o ~/Dropbox/NewCo-Shared/2.Dev.Works/db\ dumps/$(DATE).dump '$(PGDUMPURL)'
	cp  ~/Dropbox/NewCo-Shared/2.Dev.Works/db\ dumps/{$(DATE).dump,latest.dump}

pg_prod2staging:
	heroku pg:reset DATABASE --confirm newco-staging
	heroku pgbackups:restore DATABASE '$(PGDUMPURL)' --confirm newco-staging

# TODO: add additional commands to manage stuff.
# Static stuff

#all: recreate-static

#recreate-static: clean-static create-static

#create-static:
#	./manage.py collectstatic --noinput

#clean-static:
#	echo rm -rf $(dirname $(shell ./manage.py findstatic site.js))
