from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """
            Tests waiting for database when database is available
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as getitem:
            getitem.return_value = True
            call_command('wait_for_db')

            self.assertEqual(getitem.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, time_sleep):
        """
            Tests waiting for database
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as getitem:
            getitem.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')

            self.assertEqual(getitem.call_count, 6)
