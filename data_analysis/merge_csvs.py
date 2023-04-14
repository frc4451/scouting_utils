import os
import pandas as pd
import argparse

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

def group_by_and_sort(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Given a `df` and a list of `columns`, we check to make sure the columns
    exist in the dataframe, but then apply a groupby and drop_duplicates on
    `columns` in order to get a unique list of robots and their match results.

    Parameters
    df: pd.DataFrame -- dataframe that assumes is all match data
    columns: list(str) -- list of columns we expect to see in the df and can
        be used for groupby and drop_duplicate operations.
    
    Returns
    Pandas Dataframe that should be deduplicated given `df` and `columns`.
    """
    if not all(col in df.columns for col in columns):
        raise ValueError(f"Missing required column in DataFrame: {columns}")

    grouped = df.groupby(columns)

    deduplicated = grouped.apply(lambda x: x.drop_duplicates(subset=columns))

    result = pd.concat([df for _, df in deduplicated.groupby(level=0)], ignore_index=True)

    return result    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str,
                        help='Input directory path. Expects directory with CSVs we plan to utilize.', required=True)
    parser.add_argument('-o', '--output', type=str,
                        help='Output file path. If the file or path does not exist, we will create the path needed.', required=True)
    args = parser.parse_args()
    directory = args.directory
    output = args.output

    # Combine results from all CSVs in the directory path provided.
    combined_df = read_csv_from_directory(directory=directory)

    # Group each record based on the columns we specify
    grouped_by_df = group_by_and_sort(df=combined_df, columns=['match_number', 'team_alliance', 'team_position'])

    if os.path.dirname(output):
        os.makedirs(os.path.dirname(output), exist_ok=True)
    grouped_by_df.to_csv(output, index=False)
        