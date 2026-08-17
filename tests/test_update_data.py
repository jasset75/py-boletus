import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.update_data import update_data


LOCAL_CSV = """DATE,N1,N2,N3,N4,N5,N6,NC,R
14/04/2026,15,17,18,22,32,43,21,6
13/04/2026,09,12,16,18,26,38,39,1
"""

REMOTE_CSV = """FECHA,COMB. GANADORA,,,,,,COMP.,R.
16/04/2026,01,02,03,04,05,06,07,8
15/04/2026,08,09,10,11,12,13,14,9
14/04/2026,15,17,18,22,32,43,21,6
"""

REMOTE_WITHOUT_NEW_ROWS = """FECHA,COMB. GANADORA,,,,,,COMP.,R.
14/04/2026,15,17,18,22,32,43,21,6
13/04/2026,09,12,16,18,26,38,39,1
"""


class UpdateDataTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / 'ES-bonoloto.csv'
        self.data_file.write_text(LOCAL_CSV, encoding='utf-8')

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch('core.update_data._download_remote_csv', return_value=REMOTE_CSV)
    def test_adds_only_new_rows_in_descending_order(self, _download):
        added = update_data(self.data_file)

        self.assertEqual(added, 2)
        lines = self.data_file.read_text(encoding='utf-8').splitlines()
        self.assertEqual(lines[1].split(',')[0], '16/04/2026')
        self.assertEqual(lines[2].split(',')[0], '15/04/2026')
        self.assertEqual(lines[3].split(',')[0], '14/04/2026')

    @patch(
        'core.update_data._download_remote_csv',
        return_value='<html>temporary error</html>',
    )
    def test_keeps_local_file_when_download_is_invalid(self, _download):
        before = self.data_file.read_bytes()

        with self.assertRaisesRegex(ValueError, 'Unexpected remote header'):
            update_data(self.data_file)

        self.assertEqual(self.data_file.read_bytes(), before)

    @patch(
        'core.update_data._download_remote_csv',
        return_value=REMOTE_WITHOUT_NEW_ROWS,
    )
    def test_does_not_rewrite_file_when_there_are_no_new_rows(self, _download):
        before = self.data_file.read_bytes()

        added = update_data(self.data_file)

        self.assertEqual(added, 0)
        self.assertEqual(self.data_file.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
