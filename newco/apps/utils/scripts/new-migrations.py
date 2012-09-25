from django.conf import settings
from south import migration
from south.models import MigrationHistory
import sys

apps = list(migration.all_migrations())

applied_migrations = MigrationHistory.objects.filter(app_name__in=[app.app_label() for app in apps])
applied_migrations = ['%s.%s' % (mi.app_name, mi.migration) for mi in applied_migrations]
unapplied_migrations = []

num_new_migrations = 0
for app in apps:
    for migration in app:
        if migration.app_label() + "." + migration.name() not in applied_migrations:
            num_new_migrations = num_new_migrations + 1
            unapplied_migrations.append('%s.%s' % (migration.app_label(), migration.name()))

if num_new_migrations > 0:
    sys.exit("%d new migrations to apply:\n%s" % (num_new_migrations, unapplied_migrations))
print "No migrations to run."
