import sys, re
from django.core.management.base import BaseCommand
from optparse import make_option
from django.conf import settings
from django.core.management import call_command
from StringIO import StringIO
from collections import defaultdict
from south.db import db


class StringIOisatty(StringIO):
    # need to fake a tty to preserve syntax highlighting
    def isatty(self):
        return True


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help=('Tells Django to NOT prompt the user for input of any kind. '
                  'The eventual SQL diff won`t be applied.')),
    )
    args = ''
    help = ('SQLdiffall executes sqldiff for each application, gather the'
        ' resulting \nSQL code and tries to execute it if there isn\'t any'
        ' missing table.')

    def handle(self, *args, **options):
        failed = False
        failed_number = 0
        failed_msg = defaultdict(list)
        sql = ''
        nothing_to_do = False

        for appname in settings.INSTALLED_APPS:
            if '.' in appname:
                appname = appname.split('.')[-1]
            orig_stdout = sys.stdout
            try:
                content = StringIOisatty()
                error = StringIOisatty()
                sys.stdout = content
                call_command('sqldiff', appname, stderr=error)
            except:
                failed_number += 1
                msg = error.getvalue().replace('\n', '').replace(appname, '<app_name>')
                failed_msg[msg].append(appname)

                failed = True
            finally:
                sys.stdout = orig_stdout
                out = content.getvalue()
            if not failed:
                self.stdout.write("Looked up for " + appname + '\n')
                if '-- No differences' not in out:
                    sql += out.replace('\x1b[33mBEGIN;\x1b[0m\n', '').replace('\x1b[33mCOMMIT;\x1b[0m\n', '')
                else: no_diff_msg = out
            failed = False

        if sql == '':
            sql = no_diff_msg
            nothing_to_do = True
        self.stdout.write("Done.\n")
        if failed_number > 0:
            self.stdout.write("{} apps weren't diffed:\n".format(failed_number))
            self.stdout.write('\n'.join(['  {1}:\n  {0}'.format(k, ' '.join(iter(v))) for k, v in failed_msg.iteritems()]) + '\n')
        self.stdout.write("\nSQL diff result :\n" + sql)
        
        if 'Table missing' in sql:
            msg = ("\nThere are missing tables, make sure you did a syncdb"
                " and/or migrate because\n it's probably a bad idea to apply"
                " the above SQL code.\n")
            self.stdout.write(msg)
            return
        if not nothing_to_do and options.get('interactive', True):
            msg = ("\nWe detected some discrepancies between your models "
                "and the current database schema.\nWould you like to apply them"
                " now? Be careful this may fuck up everything. (yes I want/no): ")
            confirm = raw_input(msg)
            while 1:
                if confirm not in ('yes I want', 'no'):
                    confirm = raw_input('Please enter either "yes I want" or "no": ')
                    continue
                if confirm == 'yes I want':
                    sql = re.sub('\x1b.*?m', '', sql)
                    db.start_transaction()
                    db.execute_many(sql)
                    db.commit_transaction()
                    print 'ok'
                break
            return
