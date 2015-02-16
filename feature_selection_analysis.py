__author__ = 'susmita'
#Feature selection for clustering of high throughput microscopy images

import sys
from microscopium.screens import myofusion as myo
import skimage.io as io
import numpy as np
import glob
from pymongo import MongoClient
from microscopium import metrics as metric
from pandas import DataFrame
import scipy.stats


sys.path.append("/Users/susmita/project/husc")

"""
coll = MongoClient()['db_name']['coll_name']
db_name: string
        The name of the database in the MongoDB server.
coll_name : string
        The name of the collection within the database
    for big dataset:
        db_name = 'myofusion'
        coll_name = 'wells'
    for small dataset:
        db_name = 'myofusion_test'
        coll_name = 'wells_test'

 mongoconnect for big_data: mongod --dbpath ~/project/husc/tests/testdata/big_data/mongodb

 """




def feature_vector(file_names):
    result = []
    for im in file_names:
        image = io.imread(im)
        feature, names = myo.feature_vector_from_rgb(image)
        result.append(feature)
    return result, names


def make_index(file_names):
    indx = []
    for i in file_names:
        plate, well = myo.filename2coord(i)
        tup = (plate, well)
        indx.append(tup)
    return indx


def dataframe(file_names):
    result, names = feature_vector(file_names)
    data = np.array(result)
    index = make_index(file_names)
    df = DataFrame(data, index, names)
    return df


def intra_vs_inter_gene_dist_hist(df):
    """
    This function compares the intra vs inter gene distance score
    by dropping features:
    'original': without dropping any features
    'cells-with': The proportion of cells with each nucleus counts(each nucleus
     counts means that several nucleus count groups can be formed because a
     number of cells have the same number of nuclei)
    'frac': fraction of nuclei that expresses a particular transcription factor
    'd-neighbor': distances between the n nearest neighbors in an image of labeled
     nuclei
    'theta': angles between nearest neighbors in an image of labeled nuclei
    'cos': cosine of angles between nearest neighbors in an image of labeled nuclei
    'sin': cosine of angles between nearest neighbors in an image of labeled nuclei
    'adaptive': If there is large variation in the background intensity, adaptive or
    local threshold is used
    'intensity': Segment objects based on intensity threshold and compute properties
    'extent': the spatial extent of the well defined rigid objects is the complete
     object itself
    'euler_number': it is a scalar whose value is the total number of objects in the
     image minus the total number of holes in those objects.
    'eccentricity': how elongated it is
    'area': area of an object
    'otsu-threshold': otsu's method is used to automatically perform clustering-based
     image thresholding or the reduction of a graylevel image to a binary image.
    """

    names = ['original', 'cells-with', 'frac', 'd-neighbor', 'theta', 'cos', 'sin', 'adaptive', 'solidity', 'intensity', 'extent', 'euler_number', 'eccentricity', 'area', 'otsu-threshold']
    t_stat_p_comp = []
    t_stat_comp= []
    ks_stat_p_comp = []
    ks_stat_comp = []

    coll = MongoClient()['myofusion_test']['wells_test']

    for pattern in names:
        reduced_column = [c for c in df.columns if pattern not in c.lower()]
        reduced_df = df[reduced_column]
        intra, inter = metric.gene_distance_score(reduced_df, coll)
        t_stat, t_stat_p = scipy.stats.ttest_ind(intra, inter) # t-test stat and Pvalues
        t_stat_p_comp.append(t_stat_p)
        t_stat_comp.append(t_stat)
        ks_stat, ks_stat_p = scipy.stats.ks_2samp(intra, inter)# Computes the Kolmogorov-Smirnov statistic on 2 samples.
        ks_stat_p_comp.append(ks_stat_p)
        ks_stat_comp.append(ks_stat)

    final_dataframe = DataFrame({'t_stat_p_comp' : t_stat_p_comp,
                                 't_stat_comp' : t_stat_comp,
                                 'ks_stat_p_comp': ks_stat_p_comp,
                                 'ks_stat_comp' : ks_stat_comp })

    final_dataframe.index = names
    return final_dataframe



if __name__ == '__main__':
    file_names = glob.glob('*.tif')
    df = dataframe(file_names)
    df.to_csv('dataframe1.csv')
    final_data = intra_vs_inter_gene_dist_hist(df)



"""
After making the dataframe once and saving it in csv format:

df1 = DataFrame.from_csv('dataframe.csv')
df1.index = feature_selection_analysis.make_index(file_names)
final_data = intra_vs_inter_gene_dist_hist(df1)

"""




