# NewCo Legacy

NewCo was a startup project I worked on between 2012 and 2103.  
The goal was to provide a place where consumers would share informations about the products they used and loved.

While the technical aspects of building a website did materialize, the financial aspects never did. I've since worked on other projects that you can follow on [openbloc.fr](http://openbloc.fr)

[The site is still online](http://newco-prod.herokuapp.com/) as a testimony of what was tried to make an impact at that time.
It's part of my portfolio and it could maybe be reused (don't do this, the tech is too old ;) )
or serve to inspire other projects.

The development was mostly done by [AGASS007](https://github.com/AGASS007) and me ([blaze33](https://github.com/blaze33)).

# Advice to future entrepreneurs

1. Technology matters as long as it doesn't get in the way of all the rest.
2. Design, UX, marketing, communication matters a lot ! Don't call yourself NewCo,
   as in New Company, really ;)
3. People don't read, much less contribute on the Internet. You can't build your success
   on asking them to do stuff for you. Build it around what they would naturally do with
   the right tool (and build that one).
4. Choose your co-founders wisely. If your co-founder show up one day with another associate
   without having consulted you first, run ! Trust is everything.
5. Making money is a necessary evil, I've got a rent to pay, food to buy. The sooner you can break even, the better.

Have fun !

# Deploy your own fork

Nothing's nicer than working code you can actually play with. The stack is old, Django 1.4 was all the rage in 2013. This app has been designed to be easily hosted on heroku and as such I followed the [Twelve-Factor App](https://12factor.net/) guidelines.

Some recent updates have been made to let it run on the cedar-14 stack, the cedar-10 we used back in 2013 being deprecated. 
You will need a postgresql database [with hstore installed](http://stackoverflow.com/a/11584751/343834), `redis-server` needs to be installed too.

```
git clone git@github.com:blaze33/newco-legacy.git
pip install -r requirements.txt  # strongly advise to use virtualenv
export DJANGO_SETTINGS_MODULE=newco.settings.dev
export DATABASE_URL=postgres://user:pass@localhost:5432/newco
foreman start
```

Request for comments on the above run / deploy part: your feedback is welcome in [issue 1](https://github.com/blaze33/newco-legacy/issues/1)

The heroku add-ons used in production are the following ones:

    Heroku Postgres Dev
    Logentries TryIt
    MemCachier Developer
    New Relic APM Wayne
    Redis To Go Nano
    SendGrid Starter
    Sentry Developer

The app is mainly configured by environment variables, the main ones being `DJANGO_SETTINGS_MODULE=newco.settings.{production,dev}` and `DATABASE_URL`.  
The full list of the variables (which may or may not need to be configured) is as follow:
```
GUNICORN_MAX_REQUESTS=1000
SENDGRID_USERNAME=<username>
PYTHONUNBUFFERED=true
MEMCACHIER_PASSWORD=<password>
MAINTENANCE_PAGE_URL=<url>
AWS_ASSOCIATE_TAG=<tag>
REDISTOGO_URL=<url>
AWS_LOCALE=fr
COLUMNS=112
NEW_RELIC_LICENSE_KEY=<key>
SENTRY_DSN=<url>
GOOGLE_API_KEY=<key>
PYTHONHASHSEED=random
WEB_CONCURRENCY=02
_=/usr/bin/env
MIXPANEL_KEY_ID=<key>
PWD=/app
DJANGO_SETTINGS_MODULE=newco.settings.production
AWS_SECRET_ACCESS_KEY=<key>
AWS_PRODUCT_SECRET_ACCESS_KEY=<key>
GUNICORN_WORKERS=5
MEMCACHIER_USERNAME=<username>
AWS_ACCESS_KEY_ID=<key>
AWS_PRODUCT_ACCESS_KEY_ID=<key>
SENDGRID_PASSWORD=<password>
NEW_RELIC_APP_NAME=<appname>
AWS_STORAGE_BUCKET_NAME=<bucket-name>
HEROKU_POSTGRESQL_NAVY_URL=<postgres_url>
PORT=<port number>
NEW_RELIC_ID=<id>
MEMCACHIER_SERVERS=<url>
DATABASE_URL=<postgres_url>
```
