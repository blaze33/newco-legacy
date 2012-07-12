from django.conf import settings
from south.db import db
import os

print "Using " + os.environ['DJANGO_SETTINGS_MODULE'] + " settings."
print "Imported south.db"
print "Migrating " + settings.DATABASES["default"]["NAME"] + " database" + \
    " to use Django 1.4 and django-user-account.\nThe following SQL will be executed:"

sql="""
ALTER TABLE "signup_codes_signupcode" RENAME TO "account_signupcode";
ALTER TABLE "signup_codes_signupcoderesult" RENAME TO "account_signupcoderesult";
ALTER TABLE "emailconfirmation_emailaddress" RENAME TO "account_emailaddress";
ALTER TABLE "emailconfirmation_emailconfirmation" RENAME TO "account_emailconfirmation";
DROP TABLE "account_passwordreset";
ALTER TABLE "account_signupcode" ALTER COLUMN "code" TYPE varchar(64);
ALTER TABLE "account_signupcode" ADD CONSTRAINT "account_signupcode_code_key" UNIQUE ("code");
ALTER TABLE "account_emailconfirmation" RENAME COLUMN "confirmation_key" TO "key";
ALTER TABLE "account_emailconfirmation" ALTER COLUMN "key" TYPE varchar(64);
ALTER TABLE "account_emailconfirmation"	ADD UNIQUE ("key");
ALTER TABLE account_emailconfirmation ADD COLUMN created timestamp with time zone;
UPDATE account_emailconfirmation SET created = sent;
"""
sql2="""
ALTER TABLE account_emailconfirmation ALTER COLUMN created SET NOT NULL;
ALTER TABLE account_emailconfirmation ALTER COLUMN sent DROP NOT NULL;
ALTER TABLE "account_emailaddress" ADD CONSTRAINT "account_emailaddress_email_key" UNIQUE ("email");
ALTER TABLE "account_emailaddress" DROP CONSTRAINT "emailconfirmation_emailaddress_user_id_email_key";
"""
print sql

db.start_transaction()
db.execute_many(sql)
db.commit_transaction()

print sql2

db.start_transaction()
db.execute_many(sql2)
db.commit_transaction()

print "Done."
