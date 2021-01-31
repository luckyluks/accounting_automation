import os
import copy
import pandas as pd

from argparse import ArgumentParser
from transaction import Transaction


# Set constants
COLUMNS_TO_KEEP = ["Wertstellung", "Buchungstext", "Auftraggeber / Beg�nstigter", "Verwendungszweck", "Betrag (EUR)"]

EMPTY_RECORD = {
    "file_path": "",
    "data": None,
    "year": None,
    "month": None,
    "_skiprows": 0
}

class FinanceReport:
    def __init__(self, args):
        
        # set pandas settings
        pd.set_option('display.max_rows', 100)

        # create basic properties
        self.files = dict()
        self.input_path = args.input_path

        # check input path
        if not os.path.isdir(self.input_path):
            print(f"path \'{self.input_path}\' is not a directory! Quitting...")
            quit()
        else:
            input_files = os.listdir(self.input_path)
            print(f"Input path: \'{self.input_path}\'\nNumber of files: {len(input_files)}")

        # Parse input files
        for filename in input_files:

            if "csv" in filename:
                
                if "-" in filename:
                
                    pass

                elif "_" in filename:
                    filename_tokens = filename.split("_")
                    year = filename_tokens[0]
                    month = filename_tokens[1]
                    self.add_input_month(year, month, filename)

    def add_input_month(self, year, month, file):
        if year not in self.files:
            self.files[year] =  dict()
        if month not in self.files[year]:
            self.files[year][month] = copy.deepcopy(EMPTY_RECORD)
        self.files[year][month]["file_path"] = os.path.join(self.input_path, file)
        self.files[year][month]["month"] = month
        self.files[year][month]["year"] = year


    def load_data(self):
        for year in self.files:
            for month in self.files[year]:
                filename = self.files[year][month]["file_path"]
                temp_df = pd.read_csv(
                    filename,
                    skiprows=self.check_header_skiprows(filename),
                    header=1,
                    sep=";"
                )

                # clear data input (headers, format)
                self.files[year][month]["data"] = self.clear_data_input(temp_df)

                for index, row in self.files[year][month]["data"].iterrows():
                    t = Transaction(row)


    def clear_data_input(self, dataframe):

        # drop unused columns
        colums_to_drop = [column for column in dataframe.columns if not column in COLUMNS_TO_KEEP]
        dataframe.drop(colums_to_drop, axis=1, inplace=True)

        # clean headers
        dataframe = dataframe.rename({'Auftraggeber / Beg�nstigter': 'Auftraggeber'}, axis=1)
        dataframe = dataframe.rename({'Betrag (EUR)': 'Betrag'}, axis=1)

        # clean data
        dataframe = dataframe.replace(u'^�', "Ue", regex=True)
        dataframe = dataframe.replace(u'�', "ue", regex=True)
        dataframe['Betrag'] = pd.to_numeric(dataframe['Betrag'].str.replace('.', '',regex=True).replace(',', '.',regex=True))

        return dataframe


    def check_header_skiprows(self, filename, header_row_token="Buchungstag") -> int:
        """Parses CSV file to find the index of the header row

        Args:
            filename (string): the filename to check, as string
            header_row_token (string): the token to search for, as string, default "Buchungstag"

        Returns:
            line_idx (int): the header row index
        """
        with open(filename) as f:
            content = [l for l in (line.strip() for line in f) if l]
        f.close()

        for line_idx, line in enumerate(content):
            if header_row_token in line:
                return line_idx
        
        print(f"File \'{filename}\' has no header row with token \'{header_row_token}\'. Returning '-1'")
        return -1


    def get_year_total(self):

        for year in self.files:

            frames = [self.files[year][month]["data"] for month in self.files[year] if isinstance(self.files[year][month]["data"], pd.DataFrame)]

            temp_df = pd.concat(frames)


            # temp_df['Buchungstag']= pd.to_datetime(temp_df['Buchungstag'])
            # temp_df['Wertstellung']= pd.to_datetime(temp_df['Wertstellung'])

            temp_df.convert_dtypes().dtypes
            temp_df.infer_objects().dtypes
            temp_df = temp_df.sort_values(by='Wertstellung')
            print(temp_df.info())
            print(temp_df)

            print(temp_df["Betrag"].sum())
            print(temp_df.groupby(['Auftraggeber']).sum())
            print(temp_df.groupby(['Buchungstext']).sum())

            self.files[year]["total"] = temp_df

    def export_total(self):

        for year in self.files:
            self.files[year]["total"].to_csv(f'{year}_out.csv', index=True)




def main():
    """
    Run
    :return: None
    """
    # Grab command line args
    args = build_argparser().parse_args()

    # load data
    report = FinanceReport(args)
    report.load_data()

    # export and display data
    report.get_year_total()
    report.export_total()

    # print(json.dumps(report.files, indent=True)) # , sort_keys=True, indent=args.indent))
    
    print("End")


def build_argparser():
    """
    Parse command line arguments.
    :return: command line arguments
    """
    parser = ArgumentParser()
    parser.add_argument("-i", "--input_path", required=False, type=str,
                        default="files",
                        help="Path folder of files")
    return parser

if __name__ == '__main__':
    main()
    