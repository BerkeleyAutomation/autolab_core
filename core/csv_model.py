import os
import shutil
import logging
import csv

class CSVModel:
    """A generic model for CSV file reading and writing.
    """

    _KNOWN_TYPES_MAP = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool
    }

    def __init__(self, full_filename, headers_types_lst, default_entry=''):
        """Instantiates a CSVModel object.

        Parameters
        ----------
        full_filename : :obj:`str`
            The file path to a .csv file.

        headers_types_list : :obj:`list` of :obj:`tuple` of :obj:`str`, :obj:`str`
            A list of tuples, where the first element in each tuple is the
            string header for a column and the second element is that column's
            data type as a string.

        default_entry : :obj:`str`
            The default entry for cells in the CSV.

        Raises
        ------
        Exception
            If the types, headers, or default entry are not strings.
        """
        headers, types = zip(*headers_types_lst)
        headers_types = {headers[i]:types[i] for i in range(len(headers))}
        for key, val in headers_types.items():
            if type(val) != str:
                raise Exception("Types must be passed in as strings! For header {0}, type {1}".format(key, val))
            if val not in CSVModel._KNOWN_TYPES_MAP:
                raise Exception("Invalid type for header {0}. Got: {1}. Can only accept: {2}".format(key, val, CSVModel._KNOWN_TYPES_MAP.keys()))
            if key == '_uid' or key == '_default':
                raise Exception("Cannot create reserved columns _uid or _default!")
        if type(default_entry) != str:
            raise Exception('Default entry must be a string! Got: {0}'.format(default_entry))

        self._headers_types = headers_types.copy()
        self._headers = ('_uid',) + tuple(headers) + ('_default',)

        if not full_filename.endswith('.csv'):
            full_filename = '{0}.csv'.format(full_filename)

        self._full_filename = full_filename
        filename = os.path.basename(full_filename)
        file_path = os.path.dirname(full_filename)
        self._full_backup_filename = os.path.join(file_path, '.backup_{0}'.format(filename))

        self._uid = 0
        self._default_entry = default_entry

        self._table = []

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        types_row = self._headers_types.copy()
        types_row['_uid'] = 'int'
        types_row['_default'] = self._default_entry
        self._table.append(types_row)
        self._save()

    def _get_new_uid(self):
        """Get a new UID by incrementing the cached UID.

        Returns
        -------
        int
            The new UID.
        """
        return_uid = self._uid
        self._uid += 1
        return return_uid

    @property
    def num_rows(self):
        """int : The number of rows in the table.
        """
        return len(self._table) - 1

    def get_cur_uid(self):
        """Get the current UID associated with this object.

        Returns
        -------
        int
            The new UID.
        """
        return self._uid

    def _save(self):
        """Save the model to a .csv file
        """
        # if not first time saving, copy .csv to a backup
        if os.path.isfile(self._full_filename):
            shutil.copyfile(self._full_filename, self._full_backup_filename)

        # write to csv
        with open(self._full_filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=self._headers)
            writer.writeheader()
            for row in self._table:
                writer.writerow(row)

    def insert(self, data):
        """Insert a row into the .csv file.

        Parameters
        ----------
        data : :obj:`dict`
            A dictionary mapping keys (header strings) to values.

        Returns
        -------
        int
            The UID for the new row.

        Raises
        ------
        Exception
            If the value for a given header is not of the appropriate type.
        """
        row = {key:self._default_entry for key in self._headers}
        row['_uid'] = self._get_new_uid()

        for key, val in data.items():
            if key in ('_uid', '_default'):
                logging.warn("Cannot manually set columns _uid or _default of a row! Given data: {0}".format(data))
                continue
            if not isinstance(val, CSVModel._KNOWN_TYPES_MAP[self._headers_types[key]]):
                raise Exception('Data type mismatch for column {0}. Expected: {1}, got: {2}'.format(key,
                                                        CSVModel._KNOWN_TYPES_MAP[self._headers_types[key]], type(val)))
            row[key] = val

        self._table.append(row)
        self._save()
        return row['_uid']

    def update_by_uid(self, uid, data):
        """Update a row with the given data.

        Parameters
        ----------
        uid : int
            The UID of the row to update.

        data : :obj:`dict`
            A dictionary mapping keys (header strings) to values.

        Raises
        ------
        Exception
            If the value for a given header is not of the appropriate type.
        """
        row = self._table[uid+1]
        for key, val in data.items():
            if key not in self._headers:
                logging.warn("Unknown column name: {0}".format(key))
                continue
            if not isinstance(val, CSVModel._KNOWN_TYPES_MAP[self._headers_types[key]]):
                raise Exception('Data type mismatch for column {0}. Expected: {1}, got: {2}'.format(key,
                                                        CSVModel._KNOWN_TYPES_MAP[self._headers_types[key]], type(val)))
            row[key] = val
        self._save()

    def get_by_uid(self, uid):
        """Get a copy of a given row of the table.

        Parameters
        ----------
        uid : int
            The UID of the row to update.

        Returns
        -------
        :obj:`dict`
            A dictionary mapping keys (header strings) to values, which
            represents a row of the table.
        """
        return self._table[uid].copy()

    def get_by_row(self, row):
        """Get a copy of a given row of the table.

        Parameters
        ----------
        row : int
            The number of the row to update.

        Returns
        -------
        :obj:`dict`
            A dictionary mapping keys (header strings) to values, which
            represents a row of the table.
        """
        return self._table[row + 1].copy()

    def get_by_col(self, col, val):
        """Return the first row that contains the given value in the specified column,
        or None if no row contains the given value.

        Parameters
        ----------
        col : :obj:`str`
            The header string for a column.

        val : value type
            The value to match in the column.

        Returns
        -------
        :obj:`dict`
            A dictionary mapping keys (header strings) to values, which
            represents a row of the table. This row contains the given value in
            the specified column.
        """
        for i in range(self.num_rows):
            row = self._table[i + 1]
            if row[col] == val:
                return row.copy()
        return None

    def get_by_col_last(self, col, val):
        """Return the last row that contains the given value in the specified column,
        or None if no row contains the given value.

        Parameters
        ----------
        col : :obj:`str`
            The header string for a column.

        val : value type
            The value to match in the column.

        Returns
        -------
        :obj:`dict`
            A dictionary mapping keys (header strings) to values, which
            represents a row of the table. This row contains the given value in
            the specified column.
        """
        for i in range(self.num_rows, 0, -1):
            row = self._table[i]
            if row[col] == val:
                return row.copy()
        return None

    @staticmethod
    def load(full_filename):
        """Load a .csv file into a CSVModel.

        Parameters
        ----------
        full_filename : :obj:`str`
            The file path to a .csv file.

        Returns
        -------
        :obj:`CSVModel`
            The CSVModel initialized with the data in the given file.

        Raises
        ------
        Excetpion
            If the CSV file does not exist or is malformed.
        """
        with open(full_filename, 'r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            if '_uid' not in headers or '_default' not in headers:
                raise Exception("Malformed CSVModel file!")

            all_rows = [row for row in reader]
            types = all_rows[0]
            table = [types]
            default_entry = table[0]['_default']

            for i in range(1, len(all_rows)):
                raw_row = all_rows[i]
                row = {}
                for column_name in headers:
                    if raw_row[column_name] != default_entry:
                        row[column_name] = CSVModel._KNOWN_TYPES_MAP[types[column_name]](raw_row[column_name])
                    else:
                        row[column_name] = default_entry
                table.append(row)

        if len(table) == 1:
            next_valid_uid = 0
        else:
            next_valid_uid = int(table[-1]['_uid']) + 1

        headers_init = headers[1:-1]
        types_init = [types[column_name] for column_name in headers_init]

        csv_model = CSVModel(full_filename, zip(headers_init, types_init), default_entry=default_entry)
        csv_model._uid = next_valid_uid
        csv_model._table = table
        csv_model._save()
        return csv_model

    @staticmethod
    def get_or_create(full_filename, headers_types, default_entry=''):
        """Load a .csv file into a CSVModel if the file exists, or create
        a new CSVModel with the given filename if the file does not exist.

        Parameters
        ----------
        full_filename : :obj:`str`
            The file path to a .csv file.

        headers_types : :obj:`list` of :obj:`tuple` of :obj:`str`, :obj:`str`
            A list of tuples, where the first element in each tuple is the
            string header for a column and the second element is that column's
            data type as a string.

        default_entry : :obj:`str`
            The default entry for cells in the CSV.

        Returns
        -------
        :obj:`CSVModel`
            The CSVModel initialized with the data in the given file, or a new
            CSVModel tied to the filename if the file doesn't currently exist.
        """
        if os.path.isfile(full_filename):
            return CSVModel.load(full_filename)
        else:
            return CSVModel(full_filename, headers_types, default_entry=default_entry)
