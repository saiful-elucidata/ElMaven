import pandas as pd

import constants as cs
import helper_functions as hf


class CompareJsons(object):
    """
    This class compares two EIC JSON files:
    one of the file is from earlier version of El-Maven and other is the output of running a CLI
    instance for a configuration file and makes a correlation plot between same compounds.
    """

    def __init__(self, man_path, auto_path, analysis_type=cs.by_delta_rt_and_mz, n_rt=5,
                 n_mz=2, delta_rt=0.2, delta_mz=0.3, corr_cutoff=1, p_val_cutoff=0.7,
                 comparater_list=None, unique_identifier_list=None):
        if unique_identifier_list is None:
            unique_identifier_list = []
        if comparater_list is None:
            comparater_list = []
        self.man_path = man_path
        self.auto_path = auto_path
        self.analysis_type = analysis_type
        self.n_rt = n_rt
        self.n_mz = n_mz
        self.delta_rt = delta_rt
        self.delta_mz = delta_mz
        self.corr_cutoff = corr_cutoff
        self.p_val_cutoff = p_val_cutoff
        self.comparater_list = comparater_list
        self.unique_identifier_list = unique_identifier_list

    def summary_report(self):
        """
        Compares EIC JSON files and makes a correlation plot between same compounds
        :return:
        """
        correlation_plot_url = self.correlation_plot()

    def correlation_plot(self):
        """
        This function plots a scatter plot between average intensity for a group across all the
        samples in both the datasets and for each data point it shows their correlation value.
        :return: It returns a scatter plot which we generally  call correlation plot.
        """
        correlation_and_wilcox_df = self.correlation_and_wilcox()
        correlation_df = correlation_and_wilcox_df[[cs.unique_identifier_man,
                                                    cs.unique_identifier_auto, cs.corr_coff,
                                                   cs.avg_intensity_man, cs.avg_intensity_auto]]
        config_name = hf.get_basename_url(self.man_path) + hf.get_basename_url(self.auto_path)
        cor_plot = hf.get_correlation_plot(correlation_df, config_name)
        return cor_plot

    def wilcox_plot(self):
        """
        This function returns a wilcox plot, which is basically a plot betweeen logfc and
        -log10p-val for a group comparison from both the json files.
        :return: returns wilcox plot
        """
        correlation_and_wilcox_df = self.correlation_and_wilcox()
        wilcox_df = pd.DataFrame(correlation_and_wilcox_df, columns=[cs.unique_identifier_man,
                                                                     cs.unique_identifier_auto,
                                                                     cs.corr_coff, cs.p_val,
                                                                     cs.logfc_auto_to_man,
                                                                     cs.avg_intensity_man,
                                                                     cs.avg_intensity_auto])
        wilcox_df[[cs.p_val, cs.logfc_auto_to_man]] = wilcox_df[[cs.p_val, cs.logfc_auto_to_man]].\
            apply(pd.to_numeric, errors='coerce')
        wilcox_df = wilcox_df.dropna()
        wilcox_plot = hf.get_wilcox_plot(wilcox_df)
        return wilcox_plot

    def correlation_and_wilcox(self):
        """
        This function compares a group in one dataset (for example:Citrate label-1 at rt= 2.8 from
        first JSON file) with the possible groups of that compound at different rt values in
        another dataset (for example: Citrate label-1 at rt = 2.6,2.7 and 2.9 from second JSON
        files). It calculates different values for that comparison (i.e,log fold change,
        correlation plot, p-val).

        :return: It returns a datafarme consisting of following columns:- [unique_identifier_man,
        unique_identifier_auto, corr_coff, p_val,logfc_auto_to_man,avg_intensity_man].

        Example of a row in the output dataframe:
        [HMDB01487 C13-label-10 2.906111479, HMDB01487 C13-label-10 2.906111479, 1.000000,undefined,
                0.000000,2.883855e+02,2.883855e+02]
        """
        comp_dict_man = hf.json_comp_data(self.man_path)
        comp_dict_auto = hf.json_comp_data(self.auto_path)
        if self.analysis_type == cs.by_delta_rt_and_mz:
            correlation_and_wilcox_df = hf.find_correlation_and_wilcox_test_df\
                (self.unique_identifier_list, comp_dict_man, comp_dict_auto, self.comparater_list,
                 self.analysis_type, self.delta_rt, self.delta_mz)
        elif self.analysis_type == cs.by_n_closest_rt_and_mz:
            correlation_and_wilcox_df = hf.find_correlation_and_wilcox_test_df_closest_rt_and_mz(
                self.unique_identifier_list, comp_dict_man, comp_dict_auto, self.comparater_list,
                self.n_rt, self.n_mz, self.delta_rt, self.delta_mz, self.analysis_type)
        elif self.analysis_type == cs.by_closest_and_delta_rt_and_mz:
            correlation_and_wilcox_df = hf.find_correlation_and_wilcox_test_df_closest_rt_and_mz(
                self.unique_identifier_list, comp_dict_man, comp_dict_auto, self.comparater_list,
                self.n_rt, self.n_mz, self.delta_rt, self.delta_mz, self.analysis_type)
        return correlation_and_wilcox_df

    def get_outlier_plots(self, correlation_and_wilcox_df_below_cutoff):
        """
        This function makes EIC and Scatter plots for outliers below user defined cut offs for
        Correlation and p-value.

        :param correlation_and_wilcox_df_below_cutoff: It is a dataframe which has only groups below
        user defined correlation and p-val cut offs
        :return: returns three lists
        first list has EIC plots for groups which satisfies the cut off values from first json file.
        second list has EIC plots for groups which satisfies the cut off values from second json.
        third list has intensity scatter plots between groups satisfying from json file one and two.
        """
        unique_identifier_list_man_eic = correlation_and_wilcox_df_below_cutoff[
            cs.unique_identifier_man]
        unique_identifier_list_auto_eic = correlation_and_wilcox_df_below_cutoff[
            cs.unique_identifier_auto]
        unique_identifier_list_eic = [cs.compoundId, cs.tagstring, cs.meanRt]
        eic_plots_man_list = []
        eic_plots_auto_list = []
        scatter_plots_list = []
        if len(unique_identifier_list_man_eic) == len(unique_identifier_list_auto_eic):
            for (group_name_man, group_name_auto) in zip(unique_identifier_list_man_eic,
                                                         unique_identifier_list_auto_eic):
                unique_identifier_values_man = group_name_man.split("_")
                unique_identifier_values_man = (unique_identifier_values_man[0],
                                                unique_identifier_values_man[1],
                                                float(unique_identifier_values_man[2]))

                unique_identifier_values_auto = group_name_auto.split("_")
                unique_identifier_values_auto = (unique_identifier_values_auto[0],
                                                 unique_identifier_values_auto[1],
                                                 float(unique_identifier_values_auto[2]))
                eic_plot_file_name_man = "_".join([group_name_man, "man"])
                eic_plot_file_name_auto = "_".join([group_name_auto, "auto"])
                scatter_plot_file_name = "-".join([eic_plot_file_name_man, eic_plot_file_name_auto])
                eic_plot_man = hf.eicplot(
                    [unique_identifier_list_eic, unique_identifier_values_man], self.man_path,
                    eic_plot_file_name_man.replace(" ", ""))
                eic_plots_man_list.append(eic_plot_man)
                eic_plot_auto = hf.eicplot(
                    [unique_identifier_list_eic, unique_identifier_values_auto], self.auto_path,
                    eic_plot_file_name_auto.replace(" ", ""))
                scatter_plot = hf.intensityscatterplot([unique_identifier_list_eic,
                                                        unique_identifier_values_man],
                                                       [unique_identifier_list_eic,
                                                        unique_identifier_values_auto],
                                                       self.man_path, self.auto_path,
                                                       scatter_plot_file_name.replace(" ", ""))
                scatter_plots_list.append(scatter_plot)
                eic_plots_auto_list.append(eic_plot_auto)
        return eic_plots_man_list, eic_plots_auto_list, scatter_plots_list
