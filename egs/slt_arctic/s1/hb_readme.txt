* Train dur+acou with new questions: features predicting prominence removed, prominence added. (questions-radio_tobi_dur_acou_dnn_XXX.hed)
** script to remove removed features from labels, and add prominence
** change training scripts a little bit (only questions file?)

* Train prom with questions predicting prominence (questions-radio_tobi_dur_acou_dnn_XXX.hed)
** script to extract predicting features from label files, and add prominence
** add to training scripts (new step)

* At synthesis time, use predicted prominence as input to dur+acou.
** How?

* Can predicted duration be used as input to acou? Similar problem as for prominence. Would be interesting to see if using duration as one of the input parameters to acou training makes any difference. If so, using duration as input at synthesis time would affect the predicted acoustic parameters. It seems that it should? And then duration could also be modified from outside, and maybe faster or slower speech would sound better?
* They say in the "demo paper" that this is already happening.. How? It's not in the questions file?
http://homepages.inf.ed.ac.uk/s1432486/papers/Merlin_demo_paper.pdf
"""
Duration modelling
Merlin models duration using a separate
DNN to the acoustic model.  The duration model is trained on
the aligned data, to predict phone- and/or state-level durations.
At synthesis time, duration is predicted first, and is used as an
input to the acoustic model to predict the speech parameters.
"""
