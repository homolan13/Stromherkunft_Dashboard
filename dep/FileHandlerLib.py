import os
import warnings
import pysftp
import pandas as pd

class BaseFileHandler: # This is the base class for the different handlers
    def __init__(self, config_dict: dict, rm_dir: str, filename: str): # Constructor
        """
        Needs packages:
        - os
        - warnings
        - pysftp
        - pandas as pd
        
        Input:
        - config_dict: dict with keys 'host', 'port', 'user' and 'pw'
        - rm_dir: directory on remote server where file is located
        - filename: name of file
        """
        self.host = config_dict['host']
        self.port = config_dict['port']
        self.user = config_dict['user']
        self.pw = config_dict['pw']
        self.rm_dir = rm_dir
        self.filename = filename
        self.data = None
        self.localpath = os.path.join('core', '.downloads', self.filename)

    def __del__(self): # Destructor
        self.remove_file(warning=False)

    def get_file_from_server(self, ignore_warnings=True):
        if ignore_warnings:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                cnopts = pysftp.CnOpts()
                cnopts.hostkeys = None
                with pysftp.Connection(self.host, port=self.port, username=self.user, password=self.pw, cnopts=cnopts) as c:
                    c.get(f'{self.rm_dir}/{self.filename}', self.localpath)
        else:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            with pysftp.Connection(self.host, port=self.port, username=self.user, password=self.pw, cnopts=cnopts) as c:
                c.get(f'{self.rm_dir}/{self.filename}', self.localpath)
        return None

    def remove_file(self, warning=True):
        if os.path.exists(self.localpath):
            os.remove(self.localpath)
            return None
        else:
            if warning:
                print(f'Error: {self.localpath} does not exist.')
            return None

    def load_data(self): # Abstract class method
        raise NotImplementedError 

class FileHandlerLoad(BaseFileHandler):
    def __init__(self, config_dict: dict, rm_dir: str, filename: str):
        """
        Input:
        - config_dict: dict with keys 'host', 'port', 'user' and 'pw'
        - rm_dir: directory on remote server where file is located
        - filename: name of file
        """
        super().__init__(config_dict, rm_dir, filename)

    def load_data(self):
        data = pd.read_csv(self.localpath, sep='\t')
        # get swiss rows only
        data = data[data['MapCode'] == 'CH']
        data = data[data['AreaTypeCode'] == 'CTY'] # remove duplicates
        # drop unimportant columns
        data.drop(['ResolutionCode','UpdateTime','AreaTypeCode','AreaName','MapCode','AreaCode'], axis=1, inplace=True)
        # sort data
        data.sort_values('DateTime', inplace=True)
        # insert new columns date and time with pd.NA as placeholders
        data.insert(1, 'Time', pd.NA)
        data.insert(1, 'Date', pd.NA)
        # fill Date and Time with DateTime and drop DateTime
        date = [x[:11] for x in data['DateTime']]
        time = [x[11:16] for x in data['DateTime']]
        data['Date'] = date
        data['Time'] = time
        data.drop('DateTime', axis=1, inplace=True)
        data.reset_index(drop=True, inplace=True)

        self.data = data
        return data

class FileHandlerType(BaseFileHandler):
    def __init__(self, config_dict: dict, rm_dir: str, filename: str):
        """
        Input:
        - config_dict: dict with keys 'host', 'port', 'user' and 'pw'
        - rm_dir: directory on remote server where file is located
        - filename: name of file
        """
        super().__init__(config_dict, rm_dir, filename)

    def load_data(self):
        data = pd.read_csv(self.localpath, sep='\t')
        # get swiss rows only
        data = data[data['MapCode'] == 'CH']
        data = data[data['AreaTypeCode'] == 'CTY'] # remove duplicates
        # drop unimportant columns
        data.drop(['ResolutionCode','UpdateTime','AreaTypeCode','AreaName','MapCode','AreaCode','ActualConsumption'], axis=1, inplace=True)
        # sort data
        data.sort_values('DateTime', inplace=True)
        # insert new columns date and time with pd.NA as placeholders
        data.insert(1, 'Time', pd.NA)
        data.insert(1, 'Date', pd.NA)
        # fill Date and Time with DateTime and drop DateTime
        date = [x[:11] for x in data['DateTime']]
        time = [x[11:16] for x in data['DateTime']]
        data['Date'] = date
        data['Time'] = time
        data.drop('DateTime', axis=1, inplace=True)
        data.reset_index(drop=True, inplace=True)

        self.data = data
        return data

class FileHandlerUnit(BaseFileHandler):
    def __init__(self, config_dict: dict, rm_dir: str, filename: str):
        """
        Input:
        - config_dict: dict with keys 'host', 'port', 'user' and 'pw'
        - rm_dir: directory on remote server where file is located
        - filename: name of file
        """
        super().__init__(config_dict, rm_dir, filename)

    def load_data(self):
        data = pd.read_csv(self.localpath, sep='\t')
        # get swiss rows only
        data = data[data['MapCode'] == 'CH']
        data = data[data['ProductionType'] == 'Nuclear'] # select nuclear only
        # drop unimportant columns
        data.drop(['ResolutionCode','UpdateTime','AreaTypeCode','AreaName','MapCode','AreaCode','ActualConsumption','GenerationUnitEIC','ProductionType'], axis=1, inplace=True)
        # Do not sort by units here, because that will make automation more complicated
        # sort data
        data.sort_values('DateTime', inplace=True)
        # insert new columns date and time with pd.NA as placeholders
        data.insert(1, 'Time', pd.NA)
        data.insert(1, 'Date', pd.NA)
        # fill Date and Time with DateTime and drop DateTime
        date = [x[:11] for x in data['DateTime']]
        time = [x[11:16] for x in data['DateTime']]
        data['Date'] = date
        data['Time'] = time
        data.drop('DateTime', axis=1, inplace=True)
        data.reset_index(drop=True, inplace=True)

        self.data = data
        return data

class FileHandlerOutages(BaseFileHandler):
    def __init__(self, config_dict: dict, rm_dir: str, filename: str):
        """
        Input:
        - config_dict: dict with keys 'host', 'port', 'user' and 'pw'
        - rm_dir: directory on remote server where file is located
        - filename: name of file
        """
        super().__init__(config_dict, rm_dir, filename)

    def load_data(self):
        data = pd.read_csv(self.localpath, sep='\t')
        # get swiss rows only
        data = data[data['MapCode'] == 'CH']
        data = data[data['AreaTypeCode'] == 'BZN'] # remove duplicates
        data = data[data['ProductionType'] == 'Nuclear '] # select nuclear only, watch out for the necessary whitespace after the word
        # drop unimportant columns
        data.drop(['StartTS','EndTS','TimeZone','Status','MRID','AreaCode','AreaTypeCode','AreaName','MapCode','PowerResourceEIC','ProductionType','InstalledCapacity','AvailableCapacity','Version','UpdateTime'], axis=1, inplace=True)
        # sort data
        data.drop_duplicates(inplace=True) # drop duplicates
        data.sort_values('EndOutage', inplace=True, ascending=False) # sort by EndOutage and drop duplicates except EndOutage, keep the one that has the longest duration
        data.drop_duplicates(subset=[col for col in list(data.columns) if col != 'EndOutage'], inplace=True)
        data.sort_values(['StartOutage','EndOutage'], inplace=True)
        # insert new columns date and time with pd.NA as placeholders
        data.insert(2, 'EndTime', pd.NA)
        data.insert(2, 'EndDate', pd.NA)
        data.insert(2, 'StartTime', pd.NA)
        data.insert(2, 'StartDate', pd.NA)
        # fill Date and Time with DateTime and drop DateTime
        start_date = [x[:11] for x in data['StartOutage']]
        start_time = [x[11:16] for x in data['StartOutage']]
        data['StartDate'] = start_date
        data['StartTime'] = start_time
        end_date = [x[:11] for x in data['EndOutage']]
        end_time = [x[11:16] for x in data['EndOutage']]
        data['EndDate'] = end_date
        data['EndTime'] = end_time
        data.drop(['StartOutage','EndOutage'], axis=1, inplace=True)
        data.reset_index(drop=True, inplace=True)

        self.data = data
        return data

class FileHandlerFlow(BaseFileHandler):
    def __init__(self, config_dict: dict, rm_dir: str, filename: str):
        """
        Input:
        - config_dict: dict with keys 'host', 'port', 'user' and 'pw'
        - rm_dir: directory on remote server where file is located
        - filename: name of file
        """
        super().__init__(config_dict, rm_dir, filename)

    def load_data(self):
        data = pd.read_csv(self.localpath, sep='\t')
        # get swiss rows only
        data = pd.concat([data[data['OutMapCode'] == 'CH'], data[data['InMapCode'] == 'CH']], axis=0)
        data = data[data['OutAreaTypeCode'] == 'CTY']
        data = data[data['FlowValue'] != 0]
        # drop unimportant columns
        data.drop(['ResolutionCode','UpdateTime','OutAreaCode','OutAreaTypeCode','OutAreaName','InAreaTypeCode','InAreaCode','InAreaName'], axis=1, inplace=True)
        # Import = +, Export = - / Add import and exports from different countries
        data.loc[data['OutMapCode'] == 'CH', 'FlowValue'] *= -1
        data.drop(['OutMapCode','InMapCode'], axis=1, inplace=True)
        acc_flow_values = {dt: sum(data.loc[data['DateTime'] == dt, 'FlowValue']) for dt in set(data['DateTime'])}
        data.drop_duplicates(subset='DateTime', inplace=True)
        for dt in set(data['DateTime']):
            data.loc[data['DateTime'] == dt, 'FlowValue'] = acc_flow_values[dt]
        # sort data
        data.sort_values('DateTime', inplace=True)
        # insert new columns date and time with pd.NA as placeholders
        data.insert(1, 'Time', pd.NA)
        data.insert(1, 'Date', pd.NA)
        # fill Date and Time with DateTime and drop DateTime
        date = [x[:11] for x in data['DateTime']]
        time = [x[11:16] for x in data['DateTime']]
        data['Date'] = date
        data['Time'] = time
        data.drop('DateTime', axis=1, inplace=True)
        # Keep only full hour rows (some data is updated every 15 min)
        data = data[(data['Time'].str[3:] == '00')]
        data.reset_index(drop=True, inplace=True)
        
        self.data = data
        return data


### Below is the old implementation of the Filehandler
class _FileHandler:
    """
    Needs packages:
    - os
    - warnings
    - pysftp
    - pandas as pd
    
    Input:
    - config_dict: dict with keys 'host', 'port', 'user' and 'pw'
    - rm_dir: directory on remote server where file is located
    - filename: name of file
    - file_type: type has to be in ['load', 'type', 'unit', 'outages']    
    """
    def __init__(self, config_dict, rm_dir, filename, file_type):
        self.host = config_dict['host']
        self.port = config_dict['port']
        self.user = config_dict['user']
        self.pw = config_dict['pw']
        self.rm_dir = rm_dir
        self.filename = filename
        self.file_type = file_type
        assert file_type in ['load', 'type', 'unit', 'outages', 'flow'], 'Invalid file_type!'
        self.data = None
        self.localpath = os.path.join('.downloads', self.filename)

    def __del__(self):
        self.remove_file(warning=False)

    def construct_path(self):
        return f'{self.rm_dir}/{self.filename}'

    def get_file_from_server(self, ignore_warnings=True):
        if ignore_warnings:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                cnopts = pysftp.CnOpts()
                cnopts.hostkeys = None
                with pysftp.Connection(self.host, port=self.port, username=self.user, password=self.pw, cnopts=cnopts) as c:
                    c.get(self.construct_path(), self.localpath)
        else:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            with pysftp.Connection(self.host, port=self.port, username=self.user, password=self.pw, cnopts=cnopts) as c:
                c.get(self.construct_path(), self.localpath)
        return None

    def load_data(self):
        data = pd.read_csv(self.localpath, sep='\t')

        if self.file_type == 'load':

            # get swiss rows only
            data = data[data['MapCode'] == 'CH']
            data = data[data['AreaTypeCode'] == 'CTY'] # remove duplicates

            # drop unimportant columns
            data.drop(['ResolutionCode','UpdateTime','AreaTypeCode','AreaName','MapCode','AreaCode'], axis=1, inplace=True)

            # sort data
            data.sort_values('DateTime', inplace=True)

            # insert new columns date and time with pd.NA as placeholders
            data.insert(1, 'Time', pd.NA)
            data.insert(1, 'Date', pd.NA)

            # fill Date and Time with DateTime and drop DateTime
            date = [x[:11] for x in data['DateTime']]
            time = [x[11:16] for x in data['DateTime']]
            data['Date'] = date
            data['Time'] = time
            data.drop('DateTime', axis=1, inplace=True)

            data.reset_index(drop=True, inplace=True)


        if self.file_type == 'type':

            # get swiss rows only
            data = data[data['MapCode'] == 'CH']
            data = data[data['AreaTypeCode'] == 'CTY'] # remove duplicates

            # drop unimportant columns
            data.drop(['ResolutionCode','UpdateTime','AreaTypeCode','AreaName','MapCode','AreaCode','ActualConsumption'], axis=1, inplace=True)

            # sort data
            data.sort_values('DateTime', inplace=True)

            # insert new columns date and time with pd.NA as placeholders
            data.insert(1, 'Time', pd.NA)
            data.insert(1, 'Date', pd.NA)

            # fill Date and Time with DateTime and drop DateTime
            date = [x[:11] for x in data['DateTime']]
            time = [x[11:16] for x in data['DateTime']]
            data['Date'] = date
            data['Time'] = time
            data.drop('DateTime', axis=1, inplace=True)

            data.reset_index(drop=True, inplace=True)


        if self.file_type == 'unit':

            # get swiss rows only
            data = data[data['MapCode'] == 'CH']
            data = data[data['ProductionType'] == 'Nuclear'] # select nuclear only

            # drop unimportant columns
            data.drop(['ResolutionCode','UpdateTime','AreaTypeCode','AreaName','MapCode','AreaCode','ActualConsumption','GenerationUnitEIC','ProductionType'], axis=1, inplace=True)

            # XXX: Do not sort by units here, because that will make automation more complicated

            # sort data
            data.sort_values('DateTime', inplace=True)

            # insert new columns date and time with pd.NA as placeholders
            data.insert(1, 'Time', pd.NA)
            data.insert(1, 'Date', pd.NA)

            # fill Date and Time with DateTime and drop DateTime
            date = [x[:11] for x in data['DateTime']]
            time = [x[11:16] for x in data['DateTime']]
            data['Date'] = date
            data['Time'] = time
            data.drop('DateTime', axis=1, inplace=True)

            data.reset_index(drop=True, inplace=True)

        
        if self.file_type == 'outages':
            
            # get swiss rows only
            data = data[data['MapCode'] == 'CH']
            data = data[data['AreaTypeCode'] == 'BZN'] # remove duplicates
            data = data[data['ProductionType'] == 'Nuclear '] # select nuclear only, watch out for the necessary whitespace after the word

            # drop unimportant columns
            data.drop(['StartTS','EndTS','TimeZone','Status','MRID','AreaCode','AreaTypeCode','AreaName','MapCode','PowerResourceEIC','ProductionType','InstalledCapacity','AvailableCapacity','Version','UpdateTime'], axis=1, inplace=True)

            # XXX: Do not sort by units here, because that will make automation more complicated

            # sort data
            data.drop_duplicates(inplace=True) # drop duplicates
            data.sort_values('EndOutage', inplace=True, ascending=False) # sort by EndOutage and drop duplicates except EndOutage, keep the one that has the longest duration
            data.drop_duplicates(subset=[col for col in list(data.columns) if col != 'EndOutage'], inplace=True)
            data.sort_values(['StartOutage','EndOutage'], inplace=True)

            # insert new columns date and time with pd.NA as placeholders
            data.insert(2, 'EndTime', pd.NA)
            data.insert(2, 'EndDate', pd.NA)
            data.insert(2, 'StartTime', pd.NA)
            data.insert(2, 'StartDate', pd.NA)

            # fill Date and Time with DateTime and drop DateTime
            start_date = [x[:11] for x in data['StartOutage']]
            start_time = [x[11:16] for x in data['StartOutage']]
            data['StartDate'] = start_date
            data['StartTime'] = start_time
            end_date = [x[:11] for x in data['EndOutage']]
            end_time = [x[11:16] for x in data['EndOutage']]
            data['EndDate'] = end_date
            data['EndTime'] = end_time
            data.drop(['StartOutage','EndOutage'], axis=1, inplace=True)

            data.reset_index(drop=True, inplace=True)

        if self.file_type == 'flow':

            # get swiss rows only
            data = pd.concat([data[data['OutMapCode'] == 'CH'], data[data['InMapCode'] == 'CH']], axis=0)
            data = data[data['OutAreaTypeCode'] == 'CTY']
            data = data[data['FlowValue'] != 0]

            # drop unimportant columns
            data.drop(['ResolutionCode','UpdateTime','OutAreaCode','OutAreaTypeCode','OutAreaName','InAreaTypeCode','InAreaCode','InAreaName'], axis=1, inplace=True)

            # Import = +, Export = - / Add import and exports from different countries
            data.loc[data['OutMapCode'] == 'CH', 'FlowValue'] *= -1
            data.drop(['OutMapCode','InMapCode'], axis=1, inplace=True)
            acc_flow_values = {dt: sum(data.loc[data['DateTime'] == dt, 'FlowValue']) for dt in set(data['DateTime'])}
            data.drop_duplicates(subset='DateTime', inplace=True)
            for dt in set(data['DateTime']):
                data.loc[data['DateTime'] == dt, 'FlowValue'] = acc_flow_values[dt]


            # sort data
            data.sort_values('DateTime', inplace=True)

            # insert new columns date and time with pd.NA as placeholders
            data.insert(1, 'Time', pd.NA)
            data.insert(1, 'Date', pd.NA)

            # fill Date and Time with DateTime and drop DateTime
            date = [x[:11] for x in data['DateTime']]
            time = [x[11:16] for x in data['DateTime']]
            data['Date'] = date
            data['Time'] = time
            data.drop('DateTime', axis=1, inplace=True)

            # Keep only full hour rows (some data is updated every 15 min)
            data = data[(data['Time'].str[3:] == '00')]

            data.reset_index(drop=True, inplace=True)
        
        self.data = data
        return data
        
        
    def remove_file(self, warning=True):
        if os.path.exists(self.localpath):
            os.remove(self.localpath)
            return None
        else:
            if warning:
                print(f'Error: {self.localpath} does not exist.')
            return None