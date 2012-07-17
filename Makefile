##! make
# A Makefile to automate things

all:

clean:
	find . -name "*.pyc" -delete
	find . -name "*~" -delete

BRANCH = $(shell hg prompt {branch})
REMOTE_URL = $(shell git config --get remote.$(BRANCH).url)
APP = $(shell echo $(REMOTE_URL)|cut -d":" -f2|cut -d"." -f1)

SYNCDB = django-admin.py syncdb --noinput
MIGRATE = django-admin.py migrate
COLLECTSTATIC = django-admin.py collectstatic --noinput
SQLDIFFALL = django-admin.py sqldiffall --settings=newco.settings.dev

define SYNC_CMD
$(SYNCDB) && \
$(MIGRATE)
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

sqldiffall:
	heroku run '$(SQLDIFFALL)' --app $(APP)

collectstatic:
	heroku run '$(COLLECTSTATIC) --app $(APP)

heroku_bash:
	heroku run bash --app $(APP)

migrate_pinax_1: maintain_on push
	heroku run python newco/apps/utils/scripts/migrate-pinax-accounts.py --app $(APP)

migrate_pinax: migrate_pinax_1 sync maintain_off

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

# TODO: add additional commands to manage stuff.
# Static stuff

#all: recreate-static

#recreate-static: clean-static create-static

#create-static:
#	./manage.py collectstatic --noinput

#clean-static:
#	echo rm -rf $(dirname $(shell ./manage.py findstatic site.js))
