import os
import csv
import pandas as pd
import argparse

def is_csv_header(row: str) -> bool:
    """
    Helps confirm that the `-c | --columns` parameter is a valid CSV
    column header that we can use in `group_by_and_sort`
    """
    try:
        csv.Sniffer().has_header(row)
        return True
    except csv.Error:
        return False

def read_csv_from_directory(directory: str) -> pd.DataFrame():
    """ 
    Handles reading a directory, filtering only the CSVs from the directory,
    and combining them to a single Pandas DataFrame. This does not alter
    the data in any form.

    Parameters
    directory: str -- string representation of input directory path

    Returns
    Pandas DataFrame that concats all CSV files to a single entity
    """
    if not os.path.isdir(directory):
        raise ValueError(f"{directory} does not exist in your file system")

    combined_df = pd.DataFrame()

    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)

            if combined_df.empty:
                combined_df = df
            elif (list(df.columns) == list(combined_df.columns)):
                combined_df = pd.concat([combined_df, df], ignore_index=True)
            else:
                raise ValueError(f"The columns of file {filename} do not match the columns of the other files.")
    
    return combined_df

def group_by_and_sort(df: pd.DataFrame, groupby: list[str] = [], 
                      drop_duplicates: list[str] = []) -> pd.DataFrame:
    """
    Given a `df` and a list of `columns`, we check to make sure the columns
    exist in the dataframe, but then apply a groupby and drop_duplicates on
    `columns` in order to get a unique list of robots and their match results.

    Parameters
    df: pd.DataFrame -- dataframe that assumes is all match data
    groupby: list[str] -- list of columns we groupby/assign order
    drop_duplicates: list[str] -- list of columns we want to deduplicate.
    
    Returns
    Pandas Dataframe that should be deduplicated given `df` and `columns`.
    """
    all_columns = [*groupby, *drop_duplicates]
    missing_columns = [col for col in all_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required column(s) in DataFrame: {', '.join(missing_columns)}")


    grouped = df.groupby(groupby)

    deduplicated = grouped.apply(lambda x: x.drop_duplicates(subset=drop_duplicates))
    result: pd.DataFrame = pd.concat([df for _, df in deduplicated.groupby(level=0)], ignore_index=True)

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str,
                        help='Input directory path. Expects directory with CSVs we plan to utilize.', required=True)
    parser.add_argument('-o', '--output', type=str,
                        help='Output file path. If the file or path does not exist, we will create the path needed.', required=True)
    parser.add_argument('-g', '--groupby', type=str,
                        help="Columns that we expect to groupby. Expects CSV format.", required=False)
    parser.add_argument('-dd', '--drop_duplicates', type=str,
                        help="Columns that we expect to deduplicate against in each group from `groupby`. Expects CSV format.", required=False)
    args = parser.parse_args()
    directory = args.directory
    output = args.output
    groupby_input = args.groupby
    drop_duplicates_input = args.drop_duplicates

    groupby_columns: list[str] = []
    drop_duplicates_columns: list[str] = []

    # Handles groupby sanitization, we have a default list of columns we expect
    # from the scouting app data. However, you can specify your own list of
    # columns to group against. Groupby also handles order depending on the
    # position of the column in the list.
    if not groupby_input:
        groupby_columns = ['match_number', 'team_alliance', 'team_position', 'team_number']
    else:
        if not is_csv_header(groupby_input):
            raise ValueError("Group By columns parameter is not a valid CSV header")
        groupby_columns = list(csv.reader([groupby_input]))[0]
    
    # Handles drop_duplicates sanitization. By default we deduplicate on
    # columns we expect to see from the scouting app, but we can provide our
    # own list via CSV format. Drop Duplicates applies to each group, not the
    # entire dataset.
    if not drop_duplicates_input:
        drop_duplicates_columns = ['timestamp']
    else:
        if not is_csv_header(drop_duplicates_input):
            raise ValueError("Drop Duplicate columns parameter is not a valid CSV header")
        drop_duplicates_columns = list(csv.reader([drop_duplicates_input]))[0]

    # Combine results from all CSVs in the directory path provided.
    combined_df = read_csv_from_directory(directory=directory)

    # Group each record based on the columns we specify and maybe drop duplicates
    grouped_by_df = group_by_and_sort(df=combined_df, groupby=groupby_columns, 
                                      drop_duplicates=drop_duplicates_columns)

    # Write our data to the given `output` parameter
    if os.path.dirname(output):
        os.makedirs(os.path.dirname(output), exist_ok=True)
    grouped_by_df.to_csv(output, index=False)
        