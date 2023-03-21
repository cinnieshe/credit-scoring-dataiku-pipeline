import pandas as pd

df = pd.DataFrame()

# A class for performing binning based on bins settings & good bad definition
class BinningMachine:
    # A method for performing binning for the whole dataframe based on bins_settings, returns a binned_df
    def perform_binning(self, bins_settings_list):
        binned_df = df[df.columns.to_list()]

        for predictor_var_info in bins_settings_list:
            new_col_name = predictor_var_info["column"] + "_binned"
            if predictor_var_info["bins"] == "none":
                binned_df[new_col_name] = df[predictor_var_info["column"]]
            elif predictor_var_info["bins"] == "equal width":
                pass
            elif predictor_var_info["bins"] == "equal frequency":
                pass
            else:
                pass

        return binned_df
    
    # A method for performing equal width binning with a specified width
    def perform_eq_width_binning_by_width(self):
        pass
    
    # A method for performing equal width binning with a specified number of fixed-width bins
    def perform_eq_width_binning_by_num_bins(self):
        pass
    
    # A method for performing equal frequency binning with a specified frequency
    def perform_eq_freq_binning_by_freq(self):
        pass
    
    # A method for performing equal frequency binning with a specified number of fixed-frequency bins
    def perform_eq_freq_binning_by_num_bins(self):
        pass
    
    # A method for performing binning based on boundary points obtained from interactive binning
    def perform_binning_by_import_settings(self):
        pass


# A class for counting the number of good and bad samples/population in the column
class GoodBadCounter:    
    # A method to get the number of sample bad, sample indeterminate, sample good, population good, and population bad
    def get_statistics(self, dframe, good_bad_def):
        new_dframe, sample_bad_count = self.__count_sample_bad(dframe, good_bad_def["bad"])
        sample_indeterminate_count = self.__count_sample_indeterminate(new_dframe, good_bad_def["indeterminate"])
        sample_good_count = self.__count_sample_good(dframe, sample_bad_count, sample_indeterminate_count)
        good_weight = good_bad_def["good"]["weight"]
        bad_weight = good_bad_def["bad"]["weight"]
        population_good_count = self.__get_population_good(sample_good_count, good_weight)
        population_bad_count = self.__get_population_bad(sample_bad_count, bad_weight)
        return (sample_bad_count, sample_indeterminate_count, sample_good_count, good_weight, bad_weight, population_good_count, population_bad_count)
    
    # A method to count the number of sample bad
    def __count_sample_bad(self, dframe, bad_defs):
        bad_count = 0
        for bad_numeric_def in bad_defs["numerical"]:
            # count number of rows if dframe row is in bad_numeric_def range, and add to bad_count
            for a_range in bad_numeric_def["ranges"]:
                bad_count += len(dframe[(dframe[bad_numeric_def["column"]] >= a_range[0]) & (dframe[bad_numeric_def["column"]] < a_range[1])])
                # delete rows if dframe row is in bad_numeric_def range
                dframe = dframe.drop(dframe[(dframe[bad_numeric_def["column"]] >= a_range[0]) & (dframe[bad_numeric_def["column"]] < a_range[1])].index)
                
        for bad_categoric_def in bad_defs["categorical"]:
            # count number of rows if dframe row is having any one of the bad_categoric_def elements value
            for element in bad_categoric_def["elements"]:
                bad_count += len(dframe[(dframe[bad_categoric_def["column"]] == element)])
                # delete rows if dframe row has value 'element'
                dframe = dframe.drop(dframe[(dframe[bad_categoric_def["column"]] == element)].index)
        
        return (dframe, bad_count)
    
    # A method to count the number of sample indeterminate
    def __count_sample_indeterminate(self, dframe, indeterminate_defs):
        indeterminate_count = 0
        for indeterminate_numeric_def in indeterminate_defs["numerical"]:
            # count number of rows if dframe row is in indeterminate_numeric_def range, and add to indeterminate_count
            for a_range in indeterminate_numeric_def["ranges"]:
                indeterminate_count += len(dframe[(dframe[indeterminate_numeric_def["column"]] >= a_range[0]) & (dframe[indeterminate_numeric_def["column"]] < a_range[1])])
                # delete rows if dframe row is in indeterminate_numeric_def range
                dframe = dframe.drop(dframe[(dframe[indeterminate_numeric_def["column"]] >= a_range[0]) & (dframe[indeterminate_numeric_def["column"]] < a_range[1])].index)
                
        for indeterminate_categoric_def in indeterminate_defs["categorical"]:
            # count number of rows if dframe row is having any one of the indeterminate_categoric_def elements value
            for element in indeterminate_categoric_def["elements"]:
                indeterminate_count += len(dframe[(dframe[indeterminate_categoric_def["column"]] == element)])
                # delete rows if dframe row has value 'element'
                dframe = dframe.drop(dframe[(dframe[indeterminate_categoric_def["column"]] == element)].index)
        
        return indeterminate_count
    
    # A method to count the number of sample good
    def __count_sample_good(self, dframe, sample_bad_count, sample_indeterminate_count):
        return (len(dframe) - sample_bad_count - sample_indeterminate_count)
    
    # A method to count the number of population good
    def __get_population_good(self, sample_good_count, good_weight):
        return sample_good_count * good_weight
    
    # A method to count the number of population bad
    def __get_population_bad(self, sample_bad_count, bad_weight):
        return sample_bad_count * bad_weight
    


# A class for validating user inputs for good bad definitions
class GoodBadDefValidator:
    # A method to validate if numerical definitions for bad/indeterminate has overlapped
    def validate_if_numerical_def_overlapped(self, bad_numeric_list, indeterminate_numeric_list):
        for bad_numeric_def in bad_numeric_list:
            column = bad_numeric_def["column"]
            for indeterminate_numeric_def in indeterminate_numeric_list:
                # found matching column definition
                if indeterminate_numeric_def["column"] == column:
                    # Check if any overlapping definition
                    for bad_range in bad_numeric_def["ranges"]:
                        for indeterminate_range in indeterminate_numeric_def["ranges"]:
                            if bad_range[0] < indeterminate_range[0] and bad_range[1] > indeterminate_range[0]:
                                return False
                            if bad_range[0] < indeterminate_range[1] and bad_range[1] > indeterminate_range[1]:
                                return False
                            if bad_range[0] == indeterminate_range[0] and bad_range[1] <= indeterminate_range[1]:
                                return False
                            if bad_range[1] == indeterminate_range[1] and bad_range[0] >= indeterminate_range[0]:
                                return False
                    break
        return True

    # A method to validate if categorical definitions for bad/indeterminate has overlapped
    def validate_if_categorical_def_overlapped(self, bad_categoric_list, indeterminate_categoric_list):
        for bad_categoric_def in bad_categoric_list:
            column = bad_categoric_def["column"]
            for indeterminate_categoric_def in indeterminate_categoric_list:
                # found matching column definition
                if indeterminate_categoric_def["column"] == column:
                    # Check if any overlapping definition
                    for element in bad_categoric_def["elements"]:
                        if element in indeterminate_categoric_def["elements"]:
                            return False
                    break
        return True

    # A method to validate if all numerical definition range have upper bound > lower bound, if not, returns false
    def validate_numerical_bounds(self, numeric_info_list):
        for numeric_info in numeric_info_list:
            a_range = [numeric_info[1], numeric_info[2]]
            if a_range[1] <= a_range[0]:
                return False
        return True


# A class for obtaining user inputs from the section UI info
class GoodBadDefDecoder:
    # A method to translate section UI info to a list of numerical definition
    def get_numeric_def_list_from_section(self, numeric_info_list):
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
                            numeric_list[def_idx]["ranges"][def_range_idx] = [a_range[0], a_range[1]]
                            overlapped_def_range_idxes.insert(0, def_range_idx)
                        elif def_range[0] <= a_range[0] and def_range[1] >= a_range[1]:
                            has_range_overlap = True
                        elif a_range[0] <= def_range[0] and a_range[1] >= def_range[0] and a_range[1] <= def_range[1]:
                            has_range_overlap = True
                            numeric_list[def_idx]["ranges"][def_range_idx] = [a_range[0], def_range[1]]
                            overlapped_def_range_idxes.insert(0, def_range_idx)
                        elif a_range[0] >= def_range[0] and a_range[0] <= def_range[1] and a_range[1] >= def_range[1]:
                            has_range_overlap = True
                            numeric_list[def_idx]["ranges"][def_range_idx] = [def_range[0], a_range[1]]
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
        return numeric_list
    # A method to translate section UI info to a list of categorical definition

    def get_categorical_def_list_from_section(self, categoric_info_list):
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