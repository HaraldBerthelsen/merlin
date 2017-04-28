
#HB
#This file contains a main method for reading from stdin, synthesising and waiting for new input.
#Minimal changes, so everything is a bit awkward. 

#dnn_generation_hb_mod() and main_function() are exact copies of dnn_generation() and main_function() from merlin.py, except dnn_model instead of nnets_file_name is a parameter, and loading the models takes place in the main method.

#Requirements:
#Festival, SPTK, a merlin installation with slt_arctic_full

#egs/slt_arctic/s1/hb_synth_script.pl
#dumpfeats (using a slightly modified version ss_dnn/scripts/dumpfeats_hb)
#label-full.awk (modified version ss_dnn/data/resources/HB_label-full.awk)
#simple conversion script egs/slt_arctic/s1/experiments/slt_arctic_hb/hb_make_lab.pl

#egs/slt_arctic/s1/conf/test_dur_synth_slt_arctic_hb.conf
#egs/slt_arctic/s1/conf/test_synth_slt_arctic_hb.conf

#Command line:
#python src/hb_run_merlin_synthesis.py egs/slt_arctic/s1/conf/test_dur_synth_slt_arctic_hb.conf egs/slt_arctic/s1/conf/test_synth_slt_arctic_hb.conf

#A lot of paths everywhere to change..


import cPickle
import gzip
import os, sys, errno
import time
import math

import subprocess
import socket # only for socket.getfqdn()

#  numpy & theano imports need to be done in this order (only for some numpy installations, not sure why)
import numpy
#import gnumpy as gnp
# we need to explicitly import this in some cases, not sure why this doesn't get imported with numpy itself
import numpy.distutils.__config__
# and only after that can we import theano 
import theano

from utils.providers import ListDataProvider

from frontend.label_normalisation import HTSLabelNormalisation, XMLLabelNormalisation
from frontend.silence_remover import SilenceRemover
from frontend.silence_remover import trim_silence
from frontend.min_max_norm import MinMaxNormalisation
from frontend.acoustic_composition import AcousticComposition
from frontend.parameter_generation import ParameterGeneration
from frontend.mean_variance_norm import MeanVarianceNorm

# the new class for label composition and normalisation
from frontend.label_composer import LabelComposer
from frontend.label_modifier import HTSLabelModification
#from frontend.mlpg_fast import MLParameterGenerationFast

#from frontend.mlpg_fast_layer import MLParameterGenerationFastLayer


import configuration
from models.deep_rnn import DeepRecurrentNetwork

from utils.compute_distortion import DistortionComputation, IndividualDistortionComp
from utils.generate import generate_wav
from utils.learn_rates import ExpDecreaseLearningRate

from io_funcs.binary_io import  BinaryIOCollection

#import matplotlib.pyplot as plt
# our custom logging class that can also plot
#from logplot.logging_plotting import LoggerPlotter, MultipleTimeSeriesPlot, SingleWeightMatrixPlot
from logplot.logging_plotting import LoggerPlotter, MultipleSeriesPlot, SingleWeightMatrixPlot
import logging # as logging
import logging.config
import StringIO


#HB import functions from run_merlin.py
from run_merlin import *
import re

def runPreprocScripts(input_text):
    logger = logging.getLogger("preproc")

    input_text = re.sub("\"", "", input_text)
    
    command = "echo \"%s\" | perl egs/slt_arctic/s1/hb_synth_script.pl" % input_text
    #print(command)
    logger.info(command)
    os.system(command)




#def dnn_generation(valid_file_list, nnets_file_name, n_ins, n_outs, out_file_list):
def dnn_generation_hb_mod(valid_file_list, dnn_model, n_ins, n_outs, out_file_list):
    logger = logging.getLogger("dnn_generation")
    logger.debug('Starting dnn_generation')

    plotlogger = logging.getLogger("plotting")

    #dnn_model = cPickle.load(open(nnets_file_name, 'rb'))
    
    file_number = len(valid_file_list)

    for i in xrange(file_number):  #file_number
        logger.info('generating %4d of %4d: %s' % (i+1,file_number,valid_file_list[i]) )
        fid_lab = open(valid_file_list[i], 'rb')
        features = numpy.fromfile(fid_lab, dtype=numpy.float32)
        fid_lab.close()
        features = features[:(n_ins * (features.size / n_ins))]
        test_set_x = features.reshape((-1, n_ins))

        predicted_parameter = dnn_model.parameter_prediction(test_set_x)

        ### write to cmp file
        predicted_parameter = numpy.array(predicted_parameter, 'float32')
        temp_parameter = predicted_parameter
        fid = open(out_file_list[i], 'wb')
        predicted_parameter.tofile(fid)
        logger.debug('saved to %s' % out_file_list[i])
        fid.close()





#def main_function(cfg):    
#HB added external loading of nnets file, leaving everything else as is
def main_function(cfg, dnn_model):    
    
    
    # get a logger for this main function
    logger = logging.getLogger("main")
    
    # get another logger to handle plotting duties
    plotlogger = logging.getLogger("plotting")

    # later, we might do this via a handler that is created, attached and configured
    # using the standard config mechanism of the logging module
    # but for now we need to do it manually
    plotlogger.set_plot_path(cfg.plot_dir)
    
    #### parameter setting########
    hidden_layer_size = cfg.hyper_params['hidden_layer_size']
    
    
    ####prepare environment
    
    try:
        file_id_list = read_file_list(cfg.file_id_scp)
        logger.debug('Loaded file id list from %s' % cfg.file_id_scp)
    except IOError:
        # this means that open(...) threw an error
        logger.critical('Could not load file id list from %s' % cfg.file_id_scp)
        raise
    
    ###total file number including training, development, and testing
    total_file_number = len(file_id_list)
    
    data_dir = cfg.data_dir

    nn_cmp_dir       = os.path.join(data_dir, 'nn' + cfg.combined_feature_name + '_' + str(cfg.cmp_dim))
    nn_cmp_norm_dir   = os.path.join(data_dir, 'nn_norm'  + cfg.combined_feature_name + '_' + str(cfg.cmp_dim))
    
    model_dir = os.path.join(cfg.work_dir, 'nnets_model')
    gen_dir   = os.path.join(cfg.work_dir, 'gen')    

    in_file_list_dict = {}

    for feature_name in cfg.in_dir_dict.keys():
        in_file_list_dict[feature_name] = prepare_file_path_list(file_id_list, cfg.in_dir_dict[feature_name], cfg.file_extension_dict[feature_name], False)

    nn_cmp_file_list         = prepare_file_path_list(file_id_list, nn_cmp_dir, cfg.cmp_ext)
    nn_cmp_norm_file_list    = prepare_file_path_list(file_id_list, nn_cmp_norm_dir, cfg.cmp_ext)

    ###normalisation information
    norm_info_file = os.path.join(data_dir, 'norm_info' + cfg.combined_feature_name + '_' + str(cfg.cmp_dim) + '_' + cfg.output_feature_normalisation + '.dat')
	
    ### normalise input full context label
    # currently supporting two different forms of lingustic features
    # later, we should generalise this 

    if cfg.label_style == 'HTS':
        label_normaliser = HTSLabelNormalisation(question_file_name=cfg.question_file_name, add_frame_features=cfg.add_frame_features, subphone_feats=cfg.subphone_feats)
        lab_dim = label_normaliser.dimension + cfg.appended_input_dim
        logger.info('Input label dimension is %d' % lab_dim)
        suffix=str(lab_dim)
    # no longer supported - use new "composed" style labels instead
    elif cfg.label_style == 'composed':
        # label_normaliser = XMLLabelNormalisation(xpath_file_name=cfg.xpath_file_name)
        suffix='composed'

    if cfg.process_labels_in_work_dir:
        label_data_dir = cfg.work_dir
    else:
        label_data_dir = data_dir

    # the number can be removed
    binary_label_dir      = os.path.join(label_data_dir, 'binary_label_'+suffix)
    nn_label_dir          = os.path.join(label_data_dir, 'nn_no_silence_lab_'+suffix)
    nn_label_norm_dir     = os.path.join(label_data_dir, 'nn_no_silence_lab_norm_'+suffix)

    in_label_align_file_list = prepare_file_path_list(file_id_list, cfg.in_label_align_dir, cfg.lab_ext, False)
    binary_label_file_list   = prepare_file_path_list(file_id_list, binary_label_dir, cfg.lab_ext)
    nn_label_file_list       = prepare_file_path_list(file_id_list, nn_label_dir, cfg.lab_ext)
    nn_label_norm_file_list  = prepare_file_path_list(file_id_list, nn_label_norm_dir, cfg.lab_ext)
    dur_file_list            = prepare_file_path_list(file_id_list, cfg.in_dur_dir, cfg.dur_ext)
    lf0_file_list            = prepare_file_path_list(file_id_list, cfg.in_lf0_dir, cfg.lf0_ext)
    
    # to do - sanity check the label dimension here?
    
    
    
    min_max_normaliser = None
    label_norm_file = 'label_norm_%s_%d.dat' %(cfg.label_style, lab_dim)
    label_norm_file = os.path.join(label_data_dir, label_norm_file)
   
    if cfg.GenTestList:
        try:
            test_id_list = read_file_list(cfg.test_id_scp)
            logger.debug('Loaded file id list from %s' % cfg.test_id_scp)
        except IOError:
            # this means that open(...) threw an error
            logger.critical('Could not load file id list from %s' % cfg.test_id_scp)
            raise

        in_label_align_file_list = prepare_file_path_list(test_id_list, cfg.in_label_align_dir, cfg.lab_ext, False)
        binary_label_file_list   = prepare_file_path_list(test_id_list, binary_label_dir, cfg.lab_ext)
        nn_label_file_list       = prepare_file_path_list(test_id_list, nn_label_dir, cfg.lab_ext)
        nn_label_norm_file_list  = prepare_file_path_list(test_id_list, nn_label_norm_dir, cfg.lab_ext)

    if cfg.NORMLAB and (cfg.label_style == 'HTS'):
        # simple HTS labels 
    	logger.info('preparing label data (input) using standard HTS style labels')
        label_normaliser.perform_normalisation(in_label_align_file_list, binary_label_file_list, label_type=cfg.label_type)

        remover = SilenceRemover(n_cmp = lab_dim, silence_pattern = cfg.silence_pattern, label_type=cfg.label_type, remove_frame_features = cfg.add_frame_features, subphone_feats = cfg.subphone_feats)
        remover.remove_silence(binary_label_file_list, in_label_align_file_list, nn_label_file_list)

        min_max_normaliser = MinMaxNormalisation(feature_dimension = lab_dim, min_value = 0.01, max_value = 0.99)
        ###use only training data to find min-max information, then apply on the whole dataset
        if cfg.GenTestList:
            min_max_normaliser.load_min_max_values(label_norm_file)
        else:
            min_max_normaliser.find_min_max_values(nn_label_file_list[0:cfg.train_file_number])
        ### enforce silence such that the normalization runs without removing silence: only for final synthesis
        if cfg.GenTestList and cfg.enforce_silence:
            min_max_normaliser.normalise_data(binary_label_file_list, nn_label_norm_file_list)
        else:
            min_max_normaliser.normalise_data(nn_label_file_list, nn_label_norm_file_list)


    if cfg.NORMLAB and (cfg.label_style == 'composed'):
        # new flexible label preprocessor
        
    	logger.info('preparing label data (input) using "composed" style labels')
        label_composer = LabelComposer()
        label_composer.load_label_configuration(cfg.label_config_file)
    
        logger.info('Loaded label configuration')
        # logger.info('%s' % label_composer.configuration.labels )

        lab_dim=label_composer.compute_label_dimension()
        logger.info('label dimension will be %d' % lab_dim)
        
        if cfg.precompile_xpaths:
            label_composer.precompile_xpaths()
        
        # there are now a set of parallel input label files (e.g, one set of HTS and another set of Ossian trees)
        # create all the lists of these, ready to pass to the label composer

        in_label_align_file_list = {}
        for label_style, label_style_required in label_composer.label_styles.iteritems():
            if label_style_required:
                logger.info('labels of style %s are required - constructing file paths for them' % label_style)
                if label_style == 'xpath':
                    in_label_align_file_list['xpath'] = prepare_file_path_list(file_id_list, cfg.xpath_label_align_dir, cfg.utt_ext, False)
                elif label_style == 'hts':
                    in_label_align_file_list['hts'] = prepare_file_path_list(file_id_list, cfg.hts_label_align_dir, cfg.lab_ext, False)
                else:
                    logger.critical('unsupported label style %s specified in label configuration' % label_style)
                    raise Exception
        
            # now iterate through the files, one at a time, constructing the labels for them 
            num_files=len(file_id_list)
            logger.info('the label styles required are %s' % label_composer.label_styles)
            
            for i in xrange(num_files):
                logger.info('making input label features for %4d of %4d' % (i+1,num_files))

                # iterate through the required label styles and open each corresponding label file

                # a dictionary of file descriptors, pointing at the required files
                required_labels={}
                
                for label_style, label_style_required in label_composer.label_styles.iteritems():
                    
                    # the files will be a parallel set of files for a single utterance
                    # e.g., the XML tree and an HTS label file
                    if label_style_required:
                        required_labels[label_style] = open(in_label_align_file_list[label_style][i] , 'r')
                        logger.debug(' opening label file %s' % in_label_align_file_list[label_style][i])

                logger.debug('label styles with open files: %s' % required_labels)
                label_composer.make_labels(required_labels,out_file_name=binary_label_file_list[i],fill_missing_values=cfg.fill_missing_values,iterate_over_frames=cfg.iterate_over_frames)
                    
                # now close all opened files
                for fd in required_labels.itervalues():
                    fd.close()
        
        
        # silence removal
        if cfg.remove_silence_using_binary_labels:
            silence_feature = 0 ## use first feature in label -- hardcoded for now
            logger.info('Silence removal from label using silence feature: %s'%(label_composer.configuration.labels[silence_feature]))
            logger.info('Silence will be removed from CMP files in same way')
            ## Binary labels have 2 roles: both the thing trimmed and the instructions for trimming: 
            trim_silence(binary_label_file_list, nn_label_file_list, lab_dim, \
                                binary_label_file_list, lab_dim, silence_feature)
        else:
            logger.info('No silence removal done')
            # start from the labels we have just produced, not trimmed versions
            nn_label_file_list = binary_label_file_list
        
        min_max_normaliser = MinMaxNormalisation(feature_dimension = lab_dim, min_value = 0.01, max_value = 0.99)
        ###use only training data to find min-max information, then apply on the whole dataset
        min_max_normaliser.find_min_max_values(nn_label_file_list[0:cfg.train_file_number])
        min_max_normaliser.normalise_data(nn_label_file_list, nn_label_norm_file_list)

    if min_max_normaliser != None and not cfg.GenTestList:
        ### save label normalisation information for unseen testing labels
        label_min_vector = min_max_normaliser.min_vector
        label_max_vector = min_max_normaliser.max_vector
        label_norm_info = numpy.concatenate((label_min_vector, label_max_vector), axis=0)
    
        label_norm_info = numpy.array(label_norm_info, 'float32')
        fid = open(label_norm_file, 'wb')
        label_norm_info.tofile(fid)
        fid.close()
        logger.info('saved %s vectors to %s' %(label_min_vector.size, label_norm_file))


    ### make output duration data
    if cfg.MAKEDUR:
    	logger.info('creating duration (output) features')
        label_type = cfg.label_type
        feature_type = cfg.dur_feature_type
        label_normaliser.prepare_dur_data(in_label_align_file_list, dur_file_list, label_type, feature_type)


    ### make output acoustic data
    if cfg.MAKECMP:
    	logger.info('creating acoustic (output) features')
        delta_win = cfg.delta_win #[-0.5, 0.0, 0.5]
        acc_win = cfg.acc_win     #[1.0, -2.0, 1.0]
        
        acoustic_worker = AcousticComposition(delta_win = delta_win, acc_win = acc_win)
        if 'dur' in cfg.in_dir_dict.keys() and cfg.AcousticModel:
            acoustic_worker.make_equal_frames(dur_file_list, lf0_file_list, cfg.in_dimension_dict)
        acoustic_worker.prepare_nn_data(in_file_list_dict, nn_cmp_file_list, cfg.in_dimension_dict, cfg.out_dimension_dict)

        if cfg.remove_silence_using_binary_labels:
            ## do this to get lab_dim:
            label_composer = LabelComposer()
            label_composer.load_label_configuration(cfg.label_config_file)
            lab_dim=label_composer.compute_label_dimension()
        
            silence_feature = 0 ## use first feature in label -- hardcoded for now
            logger.info('Silence removal from CMP using binary label file') 

            ## overwrite the untrimmed audio with the trimmed version:
            trim_silence(nn_cmp_file_list, nn_cmp_file_list, cfg.cmp_dim, 
                                binary_label_file_list, lab_dim, silence_feature)
                                
        else: ## back off to previous method using HTS labels:
            remover = SilenceRemover(n_cmp = cfg.cmp_dim, silence_pattern = cfg.silence_pattern, label_type=cfg.label_type, remove_frame_features = cfg.add_frame_features, subphone_feats = cfg.subphone_feats)
            remover.remove_silence(nn_cmp_file_list[0:cfg.train_file_number+cfg.valid_file_number], 
                                   in_label_align_file_list[0:cfg.train_file_number+cfg.valid_file_number], 
                                   nn_cmp_file_list[0:cfg.train_file_number+cfg.valid_file_number]) # save to itself

    ### save acoustic normalisation information for normalising the features back
    var_dir   = os.path.join(data_dir, 'var')
    if not os.path.exists(var_dir):
        os.makedirs(var_dir)

    var_file_dict = {}
    for feature_name in cfg.out_dimension_dict.keys():
        var_file_dict[feature_name] = os.path.join(var_dir, feature_name + '_' + str(cfg.out_dimension_dict[feature_name]))
        
    ### normalise output acoustic data
    if cfg.NORMCMP:
    	logger.info('normalising acoustic (output) features using method %s' % cfg.output_feature_normalisation)
        cmp_norm_info = None
        if cfg.output_feature_normalisation == 'MVN':
            normaliser = MeanVarianceNorm(feature_dimension=cfg.cmp_dim)
            ###calculate mean and std vectors on the training data, and apply on the whole dataset
            global_mean_vector = normaliser.compute_mean(nn_cmp_file_list[0:cfg.train_file_number], 0, cfg.cmp_dim)
            global_std_vector = normaliser.compute_std(nn_cmp_file_list[0:cfg.train_file_number], global_mean_vector, 0, cfg.cmp_dim)

            normaliser.feature_normalisation(nn_cmp_file_list[0:cfg.train_file_number+cfg.valid_file_number], 
                                             nn_cmp_norm_file_list[0:cfg.train_file_number+cfg.valid_file_number])
            cmp_norm_info = numpy.concatenate((global_mean_vector, global_std_vector), axis=0)

        elif cfg.output_feature_normalisation == 'MINMAX':        
            min_max_normaliser = MinMaxNormalisation(feature_dimension = cfg.cmp_dim)
            global_mean_vector = min_max_normaliser.compute_mean(nn_cmp_file_list[0:cfg.train_file_number])
            global_std_vector = min_max_normaliser.compute_std(nn_cmp_file_list[0:cfg.train_file_number], global_mean_vector)

            min_max_normaliser = MinMaxNormalisation(feature_dimension = cfg.cmp_dim, min_value = 0.01, max_value = 0.99)
            min_max_normaliser.find_min_max_values(nn_cmp_file_list[0:cfg.train_file_number])
            min_max_normaliser.normalise_data(nn_cmp_file_list, nn_cmp_norm_file_list)

            cmp_min_vector = min_max_normaliser.min_vector
            cmp_max_vector = min_max_normaliser.max_vector
            cmp_norm_info = numpy.concatenate((cmp_min_vector, cmp_max_vector), axis=0)

        else:
            logger.critical('Normalisation type %s is not supported!\n' %(cfg.output_feature_normalisation))
            raise
 
        cmp_norm_info = numpy.array(cmp_norm_info, 'float32')
        fid = open(norm_info_file, 'wb')
        cmp_norm_info.tofile(fid)
        fid.close()
        logger.info('saved %s vectors to %s' %(cfg.output_feature_normalisation, norm_info_file))
        
        feature_index = 0
        for feature_name in cfg.out_dimension_dict.keys():
            feature_std_vector = numpy.array(global_std_vector[:,feature_index:feature_index+cfg.out_dimension_dict[feature_name]], 'float32')

            fid = open(var_file_dict[feature_name], 'w')
            feature_var_vector = feature_std_vector**2
            feature_var_vector.tofile(fid)
            fid.close()

            logger.info('saved %s variance vector to %s' %(feature_name, var_file_dict[feature_name]))

            feature_index += cfg.out_dimension_dict[feature_name]

    train_x_file_list = nn_label_norm_file_list[0:cfg.train_file_number]
    train_y_file_list = nn_cmp_norm_file_list[0:cfg.train_file_number]
    valid_x_file_list = nn_label_norm_file_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number]    
    valid_y_file_list = nn_cmp_norm_file_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number]
    test_x_file_list  = nn_label_norm_file_list[cfg.train_file_number+cfg.valid_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]    
    test_y_file_list  = nn_cmp_norm_file_list[cfg.train_file_number+cfg.valid_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]


    # we need to know the label dimension before training the DNN
    # computing that requires us to look at the labels
    #
    # currently, there are two ways to do this
    if cfg.label_style == 'HTS':
        label_normaliser = HTSLabelNormalisation(question_file_name=cfg.question_file_name, add_frame_features=cfg.add_frame_features, subphone_feats=cfg.subphone_feats)
        lab_dim = label_normaliser.dimension + cfg.appended_input_dim

    elif cfg.label_style == 'composed':
        label_composer = LabelComposer()
        label_composer.load_label_configuration(cfg.label_config_file)
        lab_dim=label_composer.compute_label_dimension()

    logger.info('label dimension is %d' % lab_dim)

    combined_model_arch = str(len(hidden_layer_size))
    for hid_size in hidden_layer_size:
        combined_model_arch += '_' + str(hid_size)
    
    nnets_file_name = '%s/%s_%s_%d_%s_%d.%d.train.%d.%f.rnn.model' \
                      %(model_dir, cfg.combined_model_name, cfg.combined_feature_name, int(cfg.multistream_switch), 
                        combined_model_arch, lab_dim, cfg.cmp_dim, cfg.train_file_number, cfg.hyper_params['learning_rate'])


    ### DNN model training
    if cfg.TRAINDNN:

        var_dict = load_covariance(var_file_dict, cfg.out_dimension_dict)

    	logger.info('training DNN')

        fid = open(norm_info_file, 'rb')
        cmp_min_max = numpy.fromfile(fid, dtype=numpy.float32)
        fid.close()
        cmp_min_max = cmp_min_max.reshape((2, -1))
        cmp_mean_vector = cmp_min_max[0, ] 
        cmp_std_vector  = cmp_min_max[1, ]


        try:
            os.makedirs(model_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                # not an error - just means directory already exists
                pass
            else:
                logger.critical('Failed to create model directory %s' % model_dir)
                logger.critical(' OS error was: %s' % e.strerror)
                raise

        try:
            train_DNN(train_xy_file_list = (train_x_file_list, train_y_file_list), \
                      valid_xy_file_list = (valid_x_file_list, valid_y_file_list), \
                      nnets_file_name = nnets_file_name, \
                      n_ins = lab_dim, n_outs = cfg.cmp_dim, ms_outs = cfg.multistream_outs, \
                      hyper_params = cfg.hyper_params, buffer_size = cfg.buffer_size, plot = cfg.plot, var_dict = var_dict, 
                      cmp_mean_vector = cmp_mean_vector, cmp_std_vector = cmp_std_vector)
        except KeyboardInterrupt:
            logger.critical('train_DNN interrupted via keyboard')
            # Could 'raise' the exception further, but that causes a deep traceback to be printed
            # which we don't care about for a keyboard interrupt. So, just bail out immediately
            sys.exit(1)
        except:
            logger.critical('train_DNN threw an exception')
            raise
            
    
    
    if cfg.GENBNFEA:
        '''
        Please only tune on this step when you want to generate bottleneck features from DNN
        '''
        temp_dir_name = '%s_%s_%d_%d_%d_%d_%s_hidden' \
                        %(cfg.model_type, cfg.combined_feature_name, \
                          cfg.train_file_number, lab_dim, cfg.cmp_dim, \
                          len(hidden_layers_sizes), combined_model_arch)
        gen_dir = os.path.join(gen_dir, temp_dir_name)

        bottleneck_size = min(hidden_layers_sizes)
        bottleneck_index = 0
        for i in xrange(len(hidden_layers_sizes)):
            if hidden_layers_sizes(i) == bottleneck_size:
                bottleneck_index = i

    	logger.info('generating bottleneck features from DNN')

        try:
            os.makedirs(gen_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                # not an error - just means directory already exists
                pass
            else:
                logger.critical('Failed to create generation directory %s' % gen_dir)
                logger.critical(' OS error was: %s' % e.strerror)
                raise

        gen_file_id_list = file_id_list[0:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
        test_x_file_list  = nn_label_norm_file_list[0:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]    

        gen_file_list = prepare_file_path_list(gen_file_id_list, gen_dir, cfg.cmp_ext)
    
        dnn_hidden_generation(test_x_file_list, nnets_file_name, lab_dim, cfg.cmp_dim, gen_file_list, bottleneck_index)
            
    ### generate parameters from DNN
    temp_dir_name = '%s_%s_%d_%d_%d_%d_%d_%d_%d' \
                    %(cfg.combined_model_name, cfg.combined_feature_name, int(cfg.do_post_filtering), \
                      cfg.train_file_number, lab_dim, cfg.cmp_dim, \
                      len(hidden_layer_size), hidden_layer_size[0], hidden_layer_size[-1])
    gen_dir = os.path.join(gen_dir, temp_dir_name)

    gen_file_id_list = file_id_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
    test_x_file_list  = nn_label_norm_file_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]    

    if cfg.GenTestList:
        gen_file_id_list = test_id_list
        test_x_file_list = nn_label_norm_file_list
        ### comment the below line if you don't want the files in a separate folder
        gen_dir = cfg.test_synth_dir

    if cfg.DNNGEN:
    	logger.info('generating from DNN')

        try:
            os.makedirs(gen_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                # not an error - just means directory already exists
                pass
            else:
                logger.critical('Failed to create generation directory %s' % gen_dir)
                logger.critical(' OS error was: %s' % e.strerror)
                raise

        gen_file_list = prepare_file_path_list(gen_file_id_list, gen_dir, cfg.cmp_ext)
        #HB
        #This should be the only line changed in main_function
        #dnn_generation(test_x_file_list, nnets_file_name, lab_dim, cfg.cmp_dim, gen_file_list)
        logger.info("nnets_file_name is:\n%s" % nnets_file_name)
        dnn_generation_hb_mod(test_x_file_list, dnn_model, lab_dim, cfg.cmp_dim, gen_file_list)
        #HB end

    	logger.debug('denormalising generated output using method %s' % cfg.output_feature_normalisation)

        fid = open(norm_info_file, 'rb')
        cmp_min_max = numpy.fromfile(fid, dtype=numpy.float32)
        fid.close()
        cmp_min_max = cmp_min_max.reshape((2, -1))
        cmp_min_vector = cmp_min_max[0, ] 
        cmp_max_vector = cmp_min_max[1, ]

        if cfg.output_feature_normalisation == 'MVN':
            denormaliser = MeanVarianceNorm(feature_dimension = cfg.cmp_dim)
            denormaliser.feature_denormalisation(gen_file_list, gen_file_list, cmp_min_vector, cmp_max_vector)
        
        elif cfg.output_feature_normalisation == 'MINMAX':
            denormaliser = MinMaxNormalisation(cfg.cmp_dim, min_value = 0.01, max_value = 0.99, min_vector = cmp_min_vector, max_vector = cmp_max_vector)
            denormaliser.denormalise_data(gen_file_list, gen_file_list)
        else:
            logger.critical('denormalising method %s is not supported!\n' %(cfg.output_feature_normalisation))
            raise

        if cfg.AcousticModel:
            ##perform MLPG to smooth parameter trajectory
            ## lf0 is included, the output features much have vuv. 
            generator = ParameterGeneration(gen_wav_features = cfg.gen_wav_features, enforce_silence = cfg.enforce_silence)
            generator.acoustic_decomposition(gen_file_list, cfg.cmp_dim, cfg.out_dimension_dict, cfg.file_extension_dict, var_file_dict, do_MLPG=cfg.do_MLPG, cfg=cfg)    

        if cfg.DurationModel:
            ### Perform duration normalization(min. state dur set to 1) ### 
            gen_dur_list   = prepare_file_path_list(gen_file_id_list, gen_dir, cfg.dur_ext)
            gen_label_list = prepare_file_path_list(gen_file_id_list, gen_dir, cfg.lab_ext)
            in_gen_label_align_file_list = prepare_file_path_list(gen_file_id_list, cfg.in_label_align_dir, cfg.lab_ext, False)
            
            generator = ParameterGeneration(gen_wav_features = cfg.gen_wav_features)
            generator.duration_decomposition(gen_file_list, cfg.cmp_dim, cfg.out_dimension_dict, cfg.file_extension_dict)
           
            label_modifier = HTSLabelModification(silence_pattern = cfg.silence_pattern, label_type = cfg.label_type)
            label_modifier.modify_duration_labels(in_gen_label_align_file_list, gen_dur_list, gen_label_list)
            

    ### generate wav
    if cfg.GENWAV:
    	logger.info('reconstructing waveform(s)')
    	generate_wav(gen_dir, gen_file_id_list, cfg)     # generated speech
#    	generate_wav(nn_cmp_dir, gen_file_id_list, cfg)  # reference copy synthesis speech
    	
    ### setting back to original conditions before calculating objective scores ###
    if cfg.GenTestList:
        in_label_align_file_list = prepare_file_path_list(file_id_list, cfg.in_label_align_dir, cfg.lab_ext, False)
        binary_label_file_list   = prepare_file_path_list(file_id_list, binary_label_dir, cfg.lab_ext)
        gen_file_id_list = file_id_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]

    ### evaluation: RMSE and CORR for duration       
    if cfg.CALMCD and cfg.DurationModel:
    	logger.info('calculating MCD')

        ref_data_dir = os.path.join(data_dir, 'ref_data')

        ref_dur_list = prepare_file_path_list(gen_file_id_list, ref_data_dir, cfg.dur_ext)

        in_gen_label_align_file_list = in_label_align_file_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
        calculator = IndividualDistortionComp()

        valid_file_id_list = file_id_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number]
        test_file_id_list  = file_id_list[cfg.train_file_number+cfg.valid_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
            
        if cfg.remove_silence_using_binary_labels:
            untrimmed_reference_data = in_file_list_dict['dur'][cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
            trim_silence(untrimmed_reference_data, ref_dur_list, cfg.dur_dim, \
                                untrimmed_test_labels, lab_dim, silence_feature)
        else:
            remover = SilenceRemover(n_cmp = cfg.dur_dim, silence_pattern = cfg.silence_pattern, label_type=cfg.label_type, remove_frame_features = cfg.add_frame_features)
            remover.remove_silence(in_file_list_dict['dur'][cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number], in_gen_label_align_file_list, ref_dur_list)
            
        valid_dur_rmse, valid_dur_corr = calculator.compute_distortion(valid_file_id_list, ref_data_dir, gen_dir, cfg.dur_ext, cfg.dur_dim)
        test_dur_rmse, test_dur_corr = calculator.compute_distortion(test_file_id_list , ref_data_dir, gen_dir, cfg.dur_ext, cfg.dur_dim)

        logger.info('Develop: DNN -- RMSE: %.3f frames/phoneme; CORR: %.3f; ' \
                    %(valid_dur_rmse, valid_dur_corr))
        logger.info('Test: DNN -- RMSE: %.3f frames/phoneme; CORR: %.3f; ' \
                    %(test_dur_rmse, test_dur_corr))

    ### evaluation: calculate distortion        
    if cfg.CALMCD and cfg.AcousticModel:
    	logger.info('calculating MCD')

        ref_data_dir = os.path.join(data_dir, 'ref_data')

        ref_mgc_list = prepare_file_path_list(gen_file_id_list, ref_data_dir, cfg.mgc_ext)
        ref_bap_list = prepare_file_path_list(gen_file_id_list, ref_data_dir, cfg.bap_ext)
        ref_lf0_list = prepare_file_path_list(gen_file_id_list, ref_data_dir, cfg.lf0_ext)

        in_gen_label_align_file_list = in_label_align_file_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
        calculator = IndividualDistortionComp()

        spectral_distortion = 0.0
        bap_mse             = 0.0
        f0_mse              = 0.0
        vuv_error           = 0.0
        
        valid_file_id_list = file_id_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number]
        test_file_id_list  = file_id_list[cfg.train_file_number+cfg.valid_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]

        if cfg.remove_silence_using_binary_labels:
            ## get lab_dim:
            label_composer = LabelComposer()
            label_composer.load_label_configuration(cfg.label_config_file)
            lab_dim=label_composer.compute_label_dimension()

            ## use first feature in label -- hardcoded for now
            silence_feature = 0
            
            ## Use these to trim silence:
            untrimmed_test_labels = binary_label_file_list[cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]    


        if cfg.in_dimension_dict.has_key('mgc'):
            if cfg.remove_silence_using_binary_labels:
                untrimmed_reference_data = in_file_list_dict['mgc'][cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
                trim_silence(untrimmed_reference_data, ref_mgc_list, cfg.mgc_dim, \
                                    untrimmed_test_labels, lab_dim, silence_feature)
            else:
                remover = SilenceRemover(n_cmp = cfg.mgc_dim, silence_pattern = cfg.silence_pattern, label_type=cfg.label_type)
                remover.remove_silence(in_file_list_dict['mgc'][cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number], in_gen_label_align_file_list, ref_mgc_list)
            valid_spectral_distortion = calculator.compute_distortion(valid_file_id_list, ref_data_dir, gen_dir, cfg.mgc_ext, cfg.mgc_dim)
            test_spectral_distortion  = calculator.compute_distortion(test_file_id_list , ref_data_dir, gen_dir, cfg.mgc_ext, cfg.mgc_dim)
            valid_spectral_distortion *= (10 /numpy.log(10)) * numpy.sqrt(2.0)    ##MCD
            test_spectral_distortion  *= (10 /numpy.log(10)) * numpy.sqrt(2.0)    ##MCD

            
        if cfg.in_dimension_dict.has_key('bap'):
            if cfg.remove_silence_using_binary_labels:
                untrimmed_reference_data = in_file_list_dict['bap'][cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
                trim_silence(untrimmed_reference_data, ref_bap_list, cfg.bap_dim, \
                                    untrimmed_test_labels, lab_dim, silence_feature)
            else:
                remover = SilenceRemover(n_cmp = cfg.bap_dim, silence_pattern = cfg.silence_pattern, label_type=cfg.label_type)
                remover.remove_silence(in_file_list_dict['bap'][cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number], in_gen_label_align_file_list, ref_bap_list)
            valid_bap_mse        = calculator.compute_distortion(valid_file_id_list, ref_data_dir, gen_dir, cfg.bap_ext, cfg.bap_dim)
            test_bap_mse         = calculator.compute_distortion(test_file_id_list , ref_data_dir, gen_dir, cfg.bap_ext, cfg.bap_dim)
            valid_bap_mse = valid_bap_mse / 10.0    ##Cassia's bap is computed from 10*log|S(w)|. if use HTS/SPTK style, do the same as MGC
            test_bap_mse  = test_bap_mse / 10.0    ##Cassia's bap is computed from 10*log|S(w)|. if use HTS/SPTK style, do the same as MGC
                
        if cfg.in_dimension_dict.has_key('lf0'):
            if cfg.remove_silence_using_binary_labels:
                untrimmed_reference_data = in_file_list_dict['lf0'][cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number]
                trim_silence(untrimmed_reference_data, ref_lf0_list, cfg.lf0_dim, \
                                    untrimmed_test_labels, lab_dim, silence_feature)
            else:
                remover = SilenceRemover(n_cmp = cfg.lf0_dim, silence_pattern = cfg.silence_pattern, label_type=cfg.label_type)
                remover.remove_silence(in_file_list_dict['lf0'][cfg.train_file_number:cfg.train_file_number+cfg.valid_file_number+cfg.test_file_number], in_gen_label_align_file_list, ref_lf0_list)
            valid_f0_mse, valid_f0_corr, valid_vuv_error   = calculator.compute_distortion(valid_file_id_list, ref_data_dir, gen_dir, cfg.lf0_ext, cfg.lf0_dim)
            test_f0_mse , test_f0_corr, test_vuv_error    = calculator.compute_distortion(test_file_id_list , ref_data_dir, gen_dir, cfg.lf0_ext, cfg.lf0_dim)

        logger.info('Develop: DNN -- MCD: %.3f dB; BAP: %.3f dB; F0:- RMSE: %.3f Hz; CORR: %.3f; VUV: %.3f%%' \
                    %(valid_spectral_distortion, valid_bap_mse, valid_f0_mse, valid_f0_corr, valid_vuv_error*100.))
        logger.info('Test   : DNN -- MCD: %.3f dB; BAP: %.3f dB; F0:- RMSE: %.3f Hz; CORR: %.3f; VUV: %.3f%%' \
                    %(test_spectral_distortion , test_bap_mse , test_f0_mse , test_f0_corr, test_vuv_error*100.))

#END OF main_function copied from run_merlin.py




if __name__ == "__main__":

    # these things should be done even before trying to parse the command line

    # create a configuration instance
    # and get a short name for this instance
    #cfg=configuration.cfg

    #HB in this case two..
    cfg_duration=configuration.cfg
    cfg_acoustic=configuration.cfg

    #HB does this work or are they actually the same??
    
    # set up logging to use our custom class
    logging.setLoggerClass(LoggerPlotter)

    # get a logger for this main function
    logger = logging.getLogger("main")
    #HB
    #logger.addHandler(logging.StreamHandler(sys.stderr))



    

    #HB In this case there will be two configuration files, for duration and acoustics?
    #Or can they be merged, or replaced with entries here?
    #Nice to use the same config files as for training, if possible!
    if len(sys.argv) != 3:
        logger.critical('usage: hb_run_merlin_synthesis.sh [duration config file name] [acoustic config file name]')
        sys.exit(1)

    duration_config_file = sys.argv[1]
    duration_config_file = os.path.abspath(duration_config_file)
    #HB not sure if this works right, moving configure to just before main function, just in case
    #Also needs to be here for logging?
    cfg_duration.configure(duration_config_file)
    
    acoustic_config_file = sys.argv[2]
    acoustic_config_file = os.path.abspath(acoustic_config_file)
    #HB not sure if this works right, moving configure to just before main function, just in case
    #Also needs to be here for logging?
    cfg_acoustic.configure(acoustic_config_file)
    
    
    #HB is any of this needed except for information?
    # logger.info('Installation information:')
    # logger.info('  Merlin directory: '+os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))
    # logger.info('  PATH:')
    # env_PATHs = os.getenv('PATH')
    # if env_PATHs:
    #     env_PATHs = env_PATHs.split(':')
    #     for p in env_PATHs:
    #         if len(p)>0: logger.info('      '+p)
    # logger.info('  LD_LIBRARY_PATH:')
    # env_LD_LIBRARY_PATHs = os.getenv('LD_LIBRARY_PATH')
    # if env_LD_LIBRARY_PATHs:
    #     env_LD_LIBRARY_PATHs = env_LD_LIBRARY_PATHs.split(':')
    #     for p in env_LD_LIBRARY_PATHs:
    #         if len(p)>0: logger.info('      '+p)
    # logger.info('  Python version: '+sys.version.replace('\n',''))
    # logger.info('    PYTHONPATH:')
    # env_PYTHONPATHs = os.getenv('PYTHONPATH')
    # if env_PYTHONPATHs:
    #     env_PYTHONPATHs = env_PYTHONPATHs.split(':')
    #     for p in env_PYTHONPATHs:
    #         if len(p)>0:
    #             logger.info('      '+p)
    # logger.info('  Numpy version: '+numpy.version.version)
    # logger.info('  Theano version: '+theano.version.version)
    # logger.info('    THEANO_FLAGS: %s ' % os.getenv('THEANO_FLAGS'))
    # logger.info('    device: '+theano.config.device)



    
    #1) First load duration and acoustic nnet files

    print("Loading nnets files ...")
    #Load duration nnets file
    #The filename should be created from config file ?
    duration_nnets_file_name = "/media/bigdisk/git_repos/merlin/egs/slt_arctic/s1/experiments/slt_arctic_hb/duration_model/nnets_model/DNN_TANH_TANH_TANH_TANH_TANH_TANH_LINEAR__dur_0_6_1024_1024_1024_1024_1024_1024_416.5.train.1000.0.002000.rnn.model"
    #HB commented while testing
    logger.info("Loading duration nnet file:\n%s" % duration_nnets_file_name)
    #duration_dnn_model = None
    duration_dnn_model = cPickle.load(open(duration_nnets_file_name, 'rb'))

    #Load acoustic nnets file
    #The filename should be created from config file ?
    acoustic_nnets_file_name = "/media/bigdisk/git_repos/merlin/egs/slt_arctic/s1/experiments/slt_arctic_hb/acoustic_model/nnets_model/DNN_TANH_TANH_TANH_TANH_TANH_TANH_LINEAR__mgc_lf0_vuv_bap_0_6_1024_1024_1024_1024_1024_1024_425.187.train.1000.0.002000.rnn.model"
    #HB commented while testing
    logger.info("Loading acoustic nnet file:\n%s" % acoustic_nnets_file_name)
    #acoustic_dnn_model = None
    acoustic_dnn_model = cPickle.load(open(acoustic_nnets_file_name, 'rb'))

    print("Done loading nnets files.")


    #2) Then wait for input, for each line (?) first run preproccesing through festival and scripts

    while True:
        sys.stdout.write("Type some text, end with newline to synthesise.\n")
        try:
            input_text = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            sys.exit(0)

        #input_text = "This is a test"

        
            
        print input_text

        #save the label file in the appropriate place ..
        runPreprocScripts(input_text)


        #run main_function(cfg, dnn_model) twice, first for duration then for acoustic
        #Moved configure here to see if that helps
        cfg_duration.configure(duration_config_file)
        main_function(cfg_duration, duration_dnn_model)

        cfg_acoustic.configure(acoustic_config_file)
        main_function(cfg_acoustic, acoustic_dnn_model)
        #The audio should now be generated
        

        #5) Last return audio or file name ?
        #In this case it will be
        wav_file_name = "egs/slt_arctic/s1/experiments/slt_arctic_hb/test_synthesis/wav/test.wav"
        print("Generated wav file: %s" % wav_file_name)
        os.system("play %s" % wav_file_name)

        #for testing, remove when reading stdin
        #sys.exit()
