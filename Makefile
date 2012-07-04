##! make
# A Makefile to automate things

all:

clean:
	find . -name "*.pyc" -delete
	find . -name "*~" -delete

# TODO: add additional commands to manage stuff.
# Static stuff

#all: recreate-static

#recreate-static: clean-static create-static

#create-static:
#	./manage.py collectstatic --noinput

#clean-static:
#	echo rm -rf $(dirname $(shell ./manage.py findstatic site.js))
