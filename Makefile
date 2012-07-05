##! make
# A Makefile to automate things

all:

clean:
	find . -name "*.pyc" -delete
	find . -name "*~" -delete

BRANCH = $(shell hg prompt {branch})
REMOTE_URL = $(shell git config --get remote.staging.url)
APP = $(shell echo $(REMOTE_URL)|cut -d":" -f2|cut -d"." -f1)

SYNCDB = django-admin.py syncdb --noinput
MIGRATE = django-admin.py migrate
COLLECTSTATIC = django-admin.py collectstatic --noinput
SQLDIFFALL = django-admin.py sqldiffall

define SYNC_CMD
$(SYNCDB) && \
$(MIGRATE) && \
$(COLLECTSTATIC) && \
$(SQLDIFFALL)
endef

echo: clean
	@echo $(BRANCH) $(REMOTE_URL) $(APP)

maintain_on:
	heroku maintenance:on --app $(APP)

maintain_off:
	heroku maintenance:off --app $(APP)


push:
	hg bookmarks -f -r $(BRANCH) master
	hg push -b $(BRANCH) git+ssh://$(REMOTE_URL)

sync:
	heroku run '$(SYNC_CMD)' --app $(APP)

heroku_bash:
	heroku run bash --app $(APP)

migrate_pinax_1: maintain_on push heroku_bash
	heroku run python newco/apps/utils/scripts/migrate-pinax-accounts.py --app $(APP)

migrate_pinax: migrate_pinax_1 sync maintain_off

# TODO: add additional commands to manage stuff.
# Static stuff

#all: recreate-static

#recreate-static: clean-static create-static

#create-static:
#	./manage.py collectstatic --noinput

#clean-static:
#	echo rm -rf $(dirname $(shell ./manage.py findstatic site.js))
