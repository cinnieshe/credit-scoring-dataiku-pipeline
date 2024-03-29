import pandas as pd
import numpy as np
from decimal import Decimal

# A class for performing binning based on bins settings
class BinningMachine:
    # Perform equal width binning based on a specified width (for numerical column only)
    @staticmethod
    def perform_eq_width_binning_by_width(col_df, width):
        if len(col_df) == 0:
            return -1
        if col_df.isna().all().all():
            return pd.Series([None for _ in range(len(col_df))])
        if not pd.api.types.is_numeric_dtype(col_df.iloc[:, 0]): # Cannot be categorical type
            return -1
        if not (isinstance(width, int) or isinstance(width, float)) or width <= 0: # width cannot be non-numeric
            return -1
        
        min = col_df.min()
        max = col_df.max()
        num_bins = int(np.ceil((max - min) / width)) + 1
        
        bin_edges = list()
        for i in range(num_bins):
            bin_edges.append(float(Decimal(str(float(min))) + Decimal(str(width)) * i))
        
        bin_ranges = [[edge, float(Decimal(str(edge))+Decimal(str(width)))] for edge in bin_edges]
        
        binned_result = list()
        for _, row in col_df.iterrows():
            val = row.iloc[0]
            if np.isnan(val):
                binned_result.append(None)
                
            for bin_range in bin_ranges:
                if val >= bin_range[0] and val < bin_range[1]:
                    binned_result.append(f"[{bin_range[0]}, {bin_range[1]})")
                    break
        return pd.Series(binned_result)
    
    # A method to perform equal width binning based on a specified number of bins
    @staticmethod
    def perform_eq_width_binning_by_num_bins(col_df, num_bins):
        if len(col_df) == 0:
            return -1
        if col_df.isna().all().all():
            return pd.Series([None for _ in range(len(col_df))])
        if not pd.api.types.is_numeric_dtype(col_df.iloc[:, 0]): # Cannot be categorical type
            return -1
        if not isinstance(num_bins, int) or num_bins <= 0:
            return -1
        
        min = col_df.min()
        max = col_df.max()
        width = (float(max) - float(min)) / num_bins
        add_to_last_width = Decimal(str(width * 0.01)) # to include max value
        
        bin_edges = list()
        for i in range(num_bins):
            bin_edges.append(float(Decimal(str(float(min))) + Decimal(str(width)) * i))
        
        bin_ranges = [[edge, float(Decimal(str(edge))+Decimal(str(width)))] for edge in bin_edges]
        bin_ranges[len(bin_ranges)-1][1] = float(Decimal(str(add_to_last_width)) + Decimal(str(bin_ranges[len(bin_ranges)-1][1])))
        
        binned_result = list()
        for _, row in col_df.iterrows():
            val = row.iloc[0]
            if np.isnan(val):
                binned_result.append(None)
            for bin_range in bin_ranges:
                if val >= bin_range[0] and val < bin_range[1]:
                    binned_result.append(f"[{bin_range[0]}, {bin_range[1]})")
                    break
        return pd.Series(binned_result)
    
    # A method to perform equal frequency binning based on a specified frequency
    @staticmethod
    def perform_eq_freq_binning_by_freq(col_df, freq):
        if len(col_df) == 0:
            return -1
        if col_df.isna().all().all():
            return pd.Series([None for _ in range(len(col_df))])
        if not pd.api.types.is_numeric_dtype(col_df.iloc[:, 0]): # Cannot be categorical type
            return -1
        if not isinstance(freq, int) or freq <= 0 or freq > len(col_df):
            return -1
        
        
        num_bins = int(np.ceil(len(col_df)/freq))
        # print(num_bins)
        # if num_bins == 1: 
        #     print(type(col_df.iloc[:, 0]))
        #     return col_df.iloc[:, 0]
        
        # bin the col_df
        interval_li = pd.qcut(col_df.iloc[:, 0], num_bins, duplicates="drop").to_list()

        if all(not isinstance(x, pd._libs.interval.Interval) for x in interval_li):
            interval_li = [pd.Interval(float(col_df.iloc[0:1,0]), float(col_df.iloc[0:1,0])+1) for _ in interval_li]
        
        # convert to the format we want
        binned_result = list()
        for idx in range(len(interval_li)):
            if not isinstance(interval_li[idx], pd._libs.interval.Interval):
                binned_result.append(None)
            else:
                binned_result.append(f"[{interval_li[idx].left}, {interval_li[idx].right})")
        
        return pd.Series(binned_result)
    
    # A method to perform equal-frequency binning based on a specified number of bins
    @staticmethod
    def perform_eq_freq_binning_by_num_bins(col_df, num_bins):
        if len(col_df) == 0:
            return -1
        if col_df.isna().all().all():
            return pd.Series([None for _ in range(len(col_df))])
        if not pd.api.types.is_numeric_dtype(col_df.iloc[:, 0]): # Cannot be categorical type
            return -1
        if not isinstance(num_bins, int) or num_bins <= 0:
            return -1
        
        interval_li = pd.qcut(col_df.iloc[:, 0], num_bins, duplicates="drop").to_list()

        if all(not isinstance(x, pd._libs.interval.Interval) for x in interval_li):
            interval_li = [pd.Interval(float(col_df.iloc[0:1,0]), float(col_df.iloc[0:1,0])+1) for _ in interval_li]
        
        # convert to the format we want
        binned_result = list()
        for idx in range(len(interval_li)):
            if not isinstance(interval_li[idx], pd._libs.interval.Interval):
                binned_result.append(None)
            else:
                binned_result.append(f"[{interval_li[idx].left}, {interval_li[idx].right})")
        
        return pd.Series(binned_result)
    
    # A method to perform custom binning for a categorical column
    @staticmethod
    def perform_categorical_custom_binning(col_df, bins_settings):
        if len(col_df) == 0:
            return -1
        
        binned_result = list()
        
        for _, row in col_df.iterrows():
            val = row.iloc[0]
            has_assigned_bin = False
            for bin in bins_settings:
                if val in bin["elements"]:
                    binned_result.append(bin["name"])
                    has_assigned_bin = True
                    break 
            if has_assigned_bin == False: # does not belongs to any bin
                binned_result.append(None)
        
        return pd.Series(binned_result)
    
    # A method to perform custom binning for a numerical column
    @staticmethod
    def perform_numerical_custom_binning(col_df, bins_settings):
        if len(col_df) == 0:
            return -1
        
        binned_result = list()
        
        for _, row in col_df.iterrows():
            val = row.iloc[0]
            has_assigned_bin = False
            for bin in bins_settings:
                for r in bin["ranges"]:
                    if val >= r[0] and val < r[1]:
                        binned_result.append(bin["name"])
                        has_assigned_bin = True
                        break
                
            if has_assigned_bin == False: # does not belongs to any bin
                binned_result.append(None)
        
        return pd.Series(binned_result)
    
    # A method to perform binning (equal-width/equal-frequency/custom) for a single column (either categorical or numerical)
    @staticmethod
    def perform_binning_on_col(col_df, col_bins_settings):
        """
        col_bins_settings is in the form of: 
        {
            "column": "person_income",
            "type": "numerical",
            "info_val": 0.11,
            "bins": [
                {
                    "name": "0-9999, 30000-39999",
                    "ranges": [[0, 9999], [30000, 39999]],
                },
                {
                    "name": "20000-29999",
                    "ranges": [[20000, 29999]],
                },
            ],
        }
        """
        if col_bins_settings["bins"] == "none":
            if len(col_df) == 0:
                return -1
            return col_df.iloc[:, 0] # no binning
        elif isinstance(col_bins_settings["bins"], dict):  # auto binning
            if col_bins_settings["bins"]["algo"] == "equal width":
                if col_bins_settings["bins"]["method"] == "width":
                    if col_bins_settings["type"] == "numerical":
                        return BinningMachine.perform_eq_width_binning_by_width(col_df, col_bins_settings["bins"]["value"])
                    else:
                        return -1
                else: # by num of bins
                    if col_bins_settings["type"] == "numerical":
                        return BinningMachine.perform_eq_width_binning_by_num_bins(col_df, col_bins_settings["bins"]["value"])
                    else:
                        return -1
            else: # equal frequency
                if col_bins_settings["bins"]["method"] == "freq":
                    if col_bins_settings["type"] == "numerical":
                        return BinningMachine.perform_eq_freq_binning_by_freq(col_df, col_bins_settings["bins"]["value"])
                    else:
                        return -1
                else: # by num of bins
                    if col_bins_settings["type"] == "numerical":
                        return BinningMachine.perform_eq_freq_binning_by_num_bins(col_df, col_bins_settings["bins"]["value"])
                    else:
                        return -1
        else: # custom binning
            if col_bins_settings["type"] == "numerical":
                return BinningMachine.perform_numerical_custom_binning(col_df, col_bins_settings["bins"])
            else:
                return BinningMachine.perform_categorical_custom_binning(col_df, col_bins_settings["bins"])
    
    # A method that perform binning (equal-width/equal-frequency/custom) for the whole dataframe (can contain numerical/categorical columns)
    @staticmethod
    def perform_binning_on_whole_df(dframe, bins_settings_list):
        if len(dframe) == 0:
            return dframe
        
        for col in dframe.columns:
            col_df = dframe.loc[:, [col]]
            
            # Find col_bins_settings
            col_bins_settings = None
            for bins_settings in bins_settings_list:
                if bins_settings["column"] == col:
                    col_bins_settings = bins_settings
                    break
            
            # if no bins settings for the column, skip it
            if col_bins_settings == None:
                continue
            
            binned_series = BinningMachine.perform_binning_on_col(col_df, col_bins_settings)
            if not isinstance(binned_series, pd.Series): # error occurs
                return -1
            
            binned_col_name = col + "_binned"
            dframe[binned_col_name] = binned_series
        
        return dframe