# You need to put this under <app>/management/commands/run.py
# where <app> is whatever appropriate app should have this command.
# Then you can invoke it with ./manage.py run and you'll get something like:

# Performing system checks...

# SKIPPING SYSTEM CHECKS!

# SKIPPING MIGRATION CHECKS!

# September 15, 2019 - 02:42:06
# Django version 2.2.5, using settings 'app.settings'
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CONTROL-C.


from django.core.management.commands.test import Command as Test


class Command(Test):

    def check(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("SKIPPING SYSTEM CHECKS!\n"))

    def check_migrations(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("SKIPPING MIGRATION CHECKS!\n"))
