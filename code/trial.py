import pandas as pd
import numpy as np
from decimal import Decimal

# A class for merging overlapping good bad definition ranges/elements for the same type (bad or indeterminate)
class GoodBadDefDecoder:    
    # A method to translate numerical definition ranges defined by user (with/without overlapping) info to a list of numerical definition (no overlapping)
    @staticmethod
    def get_numeric_def_list_from_section(numeric_info_list):
        numeric_list = list()  # initialization

        for numeric_info in numeric_info_list:
            single_def_dict = dict()
            column = numeric_info[0]
            a_range = [numeric_info[1], numeric_info[2]]
            # The 2 bounds are valid, now check if any overlapping with previously saved data
            has_column_overlap = False
            for def_idx, saved_def in enumerate(numeric_list):
                if saved_def["column"] == column:
                    has_column_overlap = True
                    has_range_overlap = False
                    overlapped_def_range_idxes = list()
                    # Merge range to element list
                    for def_range_idx, def_range in enumerate(saved_def["ranges"]):
                        if len(overlapped_def_range_idxes) != 0:
                            a_range = numeric_list[def_idx]["ranges"][overlapped_def_range_idxes[0]]

                        if a_range[0] <= def_range[0] and a_range[1] >= def_range[1]:
                            has_range_overlap = True
                            numeric_list[def_idx]["ranges"][def_range_idx] = [
                                a_range[0], a_range[1]]
                            overlapped_def_range_idxes.insert(0, def_range_idx)
                        elif def_range[0] <= a_range[0] and def_range[1] >= a_range[1]:
                            has_range_overlap = True
                        elif a_range[0] <= def_range[0] and a_range[1] >= def_range[0] and a_range[1] <= def_range[1]:
                            has_range_overlap = True
                            numeric_list[def_idx]["ranges"][def_range_idx] = [
                                a_range[0], def_range[1]]
                            overlapped_def_range_idxes.insert(0, def_range_idx)
                        elif a_range[0] >= def_range[0] and a_range[0] <= def_range[1] and a_range[1] >= def_range[1]:
                            has_range_overlap = True
                            numeric_list[def_idx]["ranges"][def_range_idx] = [
                                def_range[0], a_range[1]]
                            overlapped_def_range_idxes.insert(0, def_range_idx)
                    if len(overlapped_def_range_idxes) != 0:
                        del overlapped_def_range_idxes[0]
                        for i in sorted(overlapped_def_range_idxes, reverse=True):
                            del numeric_list[def_idx]["ranges"][i]
                    if has_range_overlap == False:
                        numeric_list[def_idx]["ranges"].append(a_range)
                    break
            if has_column_overlap == False:
                single_def_dict["column"] = column
                single_def_dict["ranges"] = [a_range]
                numeric_list.append(single_def_dict)
        
        for idx in range(len(numeric_list)):
            numeric_list[idx]["ranges"] = GoodBadDefDecoder.sort_numerical_def_ranges(numeric_list[idx]["ranges"])
       
        return numeric_list
    
    # A method to sort a list of numerical def e.g., from [[15, 20], [1, 10], [13, 14]] to [[1, 10], [13, 14], [15, 20]].
    @staticmethod
    def sort_numerical_def_ranges(numeric_def_r):
        sorted_def_ranges = list()
        for r in numeric_def_r:
            has_appended = False
            for idx in range(len(sorted_def_ranges)):
                if r[0] < sorted_def_ranges[idx][0]:
                    sorted_def_ranges.insert(idx, r)
                    has_appended = True
                    break
            if has_appended == False:
                sorted_def_ranges.append(r)
        return sorted_def_ranges
    
    # A method to translate categorical definition elements defined by user (with/without overlapping) info to a list of categorical definition (no overlapping)
    @staticmethod
    def get_categorical_def_list_from_section(categoric_info_list):
        categoric_list = list()  # initialization
        for categoric_info in categoric_info_list:
            single_def_dict = dict()
            column = categoric_info[0]
            elements = categoric_info[1]
            # Check if any overlapping with previously saved data
            has_overlap = False
            for saved_def in categoric_list:
                if saved_def["column"] == column:
                    has_overlap = True
                    # Append element to elements list if it is not existed yet
                    for element in elements:
                        if element not in saved_def["elements"]:
                            saved_def["elements"].append(element)
                    break
            if has_overlap == False:
                single_def_dict["column"] = column
                single_def_dict["elements"] = elements
                categoric_list.append(single_def_dict)
        return categoric_list

def get_str_from_ranges(ranges):
        if not isinstance(ranges, list):
            return -1
        if len(ranges) == 0:
            return '[]'
        
        ranges = GoodBadDefDecoder.sort_numerical_def_ranges(ranges)
        
        ranges_str = "["
        ranges_str = f"{ranges_str}[{ranges[0][0]}, {ranges[0][1]})"
        for idx in range(1, len(ranges)):
            ranges_str = f"{ranges_str}, [{ranges[idx][0]}, {ranges[idx][1]})"
        ranges_str += "]"
        return ranges_str    
# A class for performing binning based on bins settings


class BinningMachine:
    # Perform equal width binning based on a specified width (for numerical column only)
    @staticmethod
    def perform_eq_width_binning_by_width(col_df, width):
        if len(col_df) == 0:
            return (-1, -1)
        if col_df.isna().all().all():
            return (-1, pd.Series([None for _ in range(len(col_df))]))
        # Cannot be categorical type
        if not pd.api.types.is_numeric_dtype(col_df.iloc[:, 0]):
            return (-1, -1)
        # width cannot be non-numeric
        if not (isinstance(width, int) or isinstance(width, float)) or width <= 0:
            return (-1, -1)

        min = col_df.min()
        max = col_df.max()
        num_bins = int(np.ceil((max - min) / width)) + 1

        bin_edges = list()
        for i in range(num_bins):
            bin_edges.append(
                float(Decimal(str(float(min))) + Decimal(str(width)) * i))

        bin_ranges = [
            [edge, float(Decimal(str(edge))+Decimal(str(width)))] for edge in bin_edges]

        binned_result = list()
        for _, row in col_df.iterrows():
            val = row.iloc[0]
            if np.isnan(val):
                binned_result.append(None)

            for bin_range in bin_ranges:
                if val >= bin_range[0] and val < bin_range[1]:
                    binned_result.append(f"[{bin_range[0]}, {bin_range[1]})")
                    break
        
        def_li = list()
        for r in bin_ranges:
            def_li.append({"name": get_str_from_ranges([r]), "ranges": [r]})
        
        return (def_li, pd.Series(binned_result))

    # A method to perform equal width binning based on a specified number of bins
    @staticmethod
    def perform_eq_width_binning_by_num_bins(col_df, num_bins):
        if len(col_df) == 0:
            return (-1, -1)
        if col_df.isna().all().all():
            return (-1, pd.Series([None for _ in range(len(col_df))]))
        # Cannot be categorical type
        if not pd.api.types.is_numeric_dtype(col_df.iloc[:, 0]):
            return (-1, -1)
        if not isinstance(num_bins, int) or num_bins <= 0:
            return (-1, -1)

        min = col_df.min()
        max = col_df.max()
        width = (float(max) - float(min)) / num_bins
        add_to_last_width = Decimal(str(width * 0.01))  # to include max value

        bin_edges = list()
        for i in range(num_bins):
            bin_edges.append(
                float(Decimal(str(float(min))) + Decimal(str(width)) * i))

        bin_ranges = [
            [edge, float(Decimal(str(edge))+Decimal(str(width)))] for edge in bin_edges]
        bin_ranges[len(bin_ranges)-1][1] = float(Decimal(str(add_to_last_width)
                                                         ) + Decimal(str(bin_ranges[len(bin_ranges)-1][1])))

        binned_result = list()
        for _, row in col_df.iterrows():
            val = row.iloc[0]
            if np.isnan(val):
                binned_result.append(None)
            for bin_range in bin_ranges:
                if val >= bin_range[0] and val < bin_range[1]:
                    binned_result.append(f"[{bin_range[0]}, {bin_range[1]})")
                    break
                
        def_li = list()
        for r in bin_ranges:
            def_li.append({"name": get_str_from_ranges([r]), "ranges": [r]})
        
        return (def_li, pd.Series(binned_result))

    # A method to perform equal frequency binning based on a specified frequency
    @staticmethod
    def perform_eq_freq_binning_by_freq(col_df, freq):
        if len(col_df) == 0:
            return (-1, -1)
        if col_df.isna().all().all():
            return (-1, pd.Series([None for _ in range(len(col_df))]))
        # Cannot be categorical type
        if not pd.api.types.is_numeric_dtype(col_df.iloc[:, 0]):
            return (-1, -1)
        if not isinstance(freq, int) or freq <= 0 or freq > len(col_df):
            return (-1, -1)

        num_bins = int(np.ceil(len(col_df)/freq))
        # print(num_bins)
        # if num_bins == 1:
        #     print(type(col_df.iloc[:, 0]))
        #     return col_df.iloc[:, 0]

        # bin the col_df
        interval_li = pd.qcut(
            col_df.iloc[:, 0], num_bins, duplicates="drop").to_list()

        if all(not isinstance(x, pd._libs.interval.Interval) for x in interval_li):
            interval_li = [pd.Interval(float(col_df.iloc[0:1, 0]), float(
                col_df.iloc[0:1, 0])+1) for _ in interval_li]

        # convert to the format we want
        binned_result = list()
        for idx in range(len(interval_li)):
            if not isinstance(interval_li[idx], pd._libs.interval.Interval):
                binned_result.append(None)
            else:
                binned_result.append(
                    f"[{interval_li[idx].left}, {interval_li[idx].right})")

        def_set = set()
        for idx in range(len(interval_li)):
            if isinstance(interval_li[idx], pd._libs.interval.Interval):
                def_set.add((interval_li[idx].left, interval_li[idx].right))
        bin_ranges = list(def_set)
        
        def_li = list()
        for r in bin_ranges:
            def_li.append({"name": get_str_from_ranges([[r[0], r[1]]]), "ranges": [[r[0], r[1]]]})
        
        return (def_li, pd.Series(binned_result))

    # A method to perform equal-frequency binning based on a specified number of bins
    @staticmethod
    def perform_eq_freq_binning_by_num_bins(col_df, num_bins):
        if len(col_df) == 0:
            return (-1, -1)
        if col_df.isna().all().all():
            return (-1, pd.Series([None for _ in range(len(col_df))]))
        # Cannot be categorical type
        if not pd.api.types.is_numeric_dtype(col_df.iloc[:, 0]):
            return (-1, -1)
        if not isinstance(num_bins, int) or num_bins <= 0:
            return (-1, -1)

        interval_li = pd.qcut(
            col_df.iloc[:, 0], num_bins, duplicates="drop").to_list()

        if all(not isinstance(x, pd._libs.interval.Interval) for x in interval_li):
            interval_li = [pd.Interval(float(col_df.iloc[0:1, 0]), float(
                col_df.iloc[0:1, 0])+1) for _ in interval_li]

        # convert to the format we want
        binned_result = list()
        for idx in range(len(interval_li)):
            if not isinstance(interval_li[idx], pd._libs.interval.Interval):
                binned_result.append(None)
            else:
                binned_result.append(
                    f"[{interval_li[idx].left}, {interval_li[idx].right})")

        def_set = set()
        for idx in range(len(interval_li)):
            if isinstance(interval_li[idx], pd._libs.interval.Interval):
                def_set.add((interval_li[idx].left, interval_li[idx].right))
        bin_ranges = list(def_set)
        
        def_li = list()
        for r in bin_ranges:
            def_li.append({"name": get_str_from_ranges([[r[0], r[1]]]), "ranges": [[r[0], r[1]]]})
        
        return (def_li, pd.Series(binned_result))

    # A method to perform custom binning for a categorical column
    @staticmethod
    def perform_categorical_custom_binning(col_df, bins_settings):
        if len(col_df) == 0:
            return (-1, -1)

        binned_result = list()

        for _, row in col_df.iterrows():
            val = row.iloc[0]
            has_assigned_bin = False
            for bin in bins_settings:
                if val in bin["elements"]:
                    binned_result.append(bin["name"])
                    has_assigned_bin = True
                    break
            if has_assigned_bin == False:  # does not belongs to any bin
                binned_result.append(None)

        return (bins_settings, pd.Series(binned_result))

    # A method to perform custom binning for a numerical column
    @staticmethod
    def perform_numerical_custom_binning(col_df, bins_settings):
        if len(col_df) == 0:
            return (-1, -1)

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

            if has_assigned_bin == False:  # does not belongs to any bin
                binned_result.append(None)

        return (bins_settings, pd.Series(binned_result))

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
                return (-1, -1)
            unique_bin = col_df.iloc[:, 0].unique().tolist()
            if col_bins_settings["type"] == "numerical":
                def_li = list()
                for bin in unique_bin:
                    def_li.append({"name": get_str_from_ranges([[bin, bin+1]]), "ranges": [[bin, bin+1]]})
            else:
                def_li = list()
                for bin in unique_bin:
                    def_li.append({"name": str([bin]), "elements": [bin]})
            return (def_li, col_df.iloc[:, 0])  # no binning
        elif isinstance(col_bins_settings["bins"], dict):  # auto binning
            if col_bins_settings["bins"]["algo"] == "equal width":
                if col_bins_settings["bins"]["method"] == "width":
                    if col_bins_settings["type"] == "numerical":
                        return BinningMachine.perform_eq_width_binning_by_width(col_df, col_bins_settings["bins"]["value"])
                    else:
                        return (-1, -1)
                else:  # by num of bins
                    if col_bins_settings["type"] == "numerical":
                        return BinningMachine.perform_eq_width_binning_by_num_bins(col_df, col_bins_settings["bins"]["value"])
                    else:
                        return (-1, -1)
            else:  # equal frequency
                if col_bins_settings["bins"]["method"] == "freq":
                    if col_bins_settings["type"] == "numerical":
                        return BinningMachine.perform_eq_freq_binning_by_freq(col_df, col_bins_settings["bins"]["value"])
                    else:
                        return (-1, -1)
                else:  # by num of bins
                    if col_bins_settings["type"] == "numerical":
                        return BinningMachine.perform_eq_freq_binning_by_num_bins(col_df, col_bins_settings["bins"]["value"])
                    else:
                        return (-1, -1)
        else:  # custom binning
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

            _, binned_series = BinningMachine.perform_binning_on_col(
                col_df, col_bins_settings)
            if not isinstance(binned_series, pd.Series):  # error occurs
                return -1

            binned_col_name = col + "_binned"
            dframe[binned_col_name] = binned_series

        return dframe
    
    
col_bins_settings = {"column": "person_age", "type": "numerical", "bins": {"algo": "equal frequency", "method": "num_bins", "value": 10}}
df = pd.read_excel("tests\\test_input_datasets\\credit_risk_dataset_generated.xlsx")
col_df = df.loc[:, [col_bins_settings["column"]]]
def_li, result = BinningMachine.perform_binning_on_col(col_df, col_bins_settings)

print("Result: ")
print(result)
print(def_li)

print(BinningMachine.perform_numerical_custom_binning(col_df, def_li))