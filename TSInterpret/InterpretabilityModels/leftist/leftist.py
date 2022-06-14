from email import header
from TSInterpret.InterpretabilityModels.leftist.learning_process.learning_process import LearningProcess
from TSInterpret.InterpretabilityModels.InterpretabilityBase import InterpretabilityBase
from TSInterpret.InterpretabilityModels.FeatureAttribution import FeatureAttribution
from TSInterpret.InterpretabilityModels.leftist.timeseries.transform_function.mean_transform import MeanTransform
from TSInterpret.InterpretabilityModels.leftist.timeseries.transform_function.rand_background_transform import RandBackgroundTransform
from TSInterpret.InterpretabilityModels.leftist.timeseries.transform_function.straightline_transform import StraightlineTransform
from TSInterpret.InterpretabilityModels.leftist.learning_process.SHAP_learning_process import SHAPLearningProcess
from TSInterpret.InterpretabilityModels.leftist.learning_process.LIME_learning_process import LIMELearningProcess
from TSInterpret.InterpretabilityModels.leftist.timeseries.segmentator.uniform_segmentator import UniformSegmentator
import matplotlib.pyplot as plt 
from TSInterpret.Models.PyTorchModel import PyTorchModel
from TSInterpret.Models.TensorflowModel import TensorFlowModel
from TSInterpret.Models.SklearnModel import SklearnModel
import numpy as np 

class LEFTIST(FeatureAttribution):
    """
    Local explainer for time series classification. Wrapper for LEFTIST from [1].

    [1] Guillemé, Maël, et al. "Agnostic local explanation for time series classification." 2019 IEEE 31st International Conference on Tools with Artificial Intelligence (ICTAI). IEEE, 2019.
    """
    def __init__(self,model_to_explain, reference_set = None,mode='time',backend='F'):
        ''' Initization.
         Arguments:
            model_to_explain: classification model to explain
            reference_set: reference set
            transform_name: name of transformer to be used
            segmentator: name of segmenator to be used
            learning_process_name: Either Lime or Shap 
            mode: time or Feature
            backend: TF, PYT or SK 
        '''
        super().__init__(model_to_explain, mode)

        self.neighbors = None
        # TODO move transform, segmentor and, learning process to EXPLAIN 
 
        self.test_x, _=reference_set
        self.backend=backend
        self.mode = mode
        self.change = False
        if mode == 'feat':
            self.change=True 
            self.test_x=self.test_x.reshape (-1,self.test_x.shape[-1], self.test_x.shape[-2])

        if backend == 'PYT':
            self.predict=PyTorchModel(self.model, self.change).predict
            
        elif backend== 'TF':
            self.predict=TensorFlowModel(self.model, self.change).predict
            #Parse test data into torch format : 
            
        elif backend=='SK': 
            self.predict=SklearnModel(self.model,self.change).predict
        else:
            #Assumption this is already a predict Function 
            print('The Predict Function was given directly')
            self.predict=self.model


    def explain(self,instance,nb_neighbors, idx_label=None, explanation_size=None,transform_name='straight', segmentator_name='uniform', learning_process_name='Lime',nb_interpretable_feature=10, random_state=0):
        """
        Compute the explanation.

        Parameters:
            instance np.array: item to be explained
            nb_neighbors (int): number of neighbors to generate.
            idx_label (int): index of label to explain. If None, return an explanation for each label.
            explanation_size (int): number of feature to use for the explanations
            transform_name str: Name of transformer
            learning_process_name str: 'Lime' or 'Shap' 
            nb_interpretable_feature int: number of desired features
            random_state int: fixes seed

        Returns:
            List: Attribution weight
        """
        self.transform = transform_name
        self.transform_name=transform_name
        self.learning_process_name = learning_process_name
        if segmentator_name=='uniform':
            self.segmentator = UniformSegmentator(nb_interpretable_feature)

        if self.mode =='feat':
            instance=instance.reshape(instance.shape[-1],instance.shape[-2])
        if self.transform_name == 'mean':
            self.transform = MeanTransform(instance)
        elif self.transform_name == 'straight_line':
            self.transform = StraightlineTransform(instance)
        else:
            self.transform = RandBackgroundTransform(instance)
            self.transform.set_background_dataset(self.test_x)
        if self.learning_process_name == 'SHAP':
            self.learning_process = SHAPLearningProcess(instance,self.predict,external_dataset=self.test_x)
        else:
            self.learning_process = LIMELearningProcess(random_state)
        # get the number of features of the simplified representation
        nb_interpretable_features, segments_interval = self.segmentator.segment(instance)

        self.transform.segments_interval = segments_interval
        
        # generate the neighbors around the instance to explain
        self.neighbors = self.learning_process.neighbors_generator.generate(nb_interpretable_features, nb_neighbors,self.transform)
        self.neighbors.values=np.array(self.neighbors.values).reshape(-1,instance.shape[0],1)
        # classify the neighbors
        self.neighbors.proba_labels =self.predict(self.neighbors.values)
        if len(self.neighbors.proba_labels[0]) == 1:
            self.neighbors.proba_labels = np.array([np.array([el[0],1-el[0]]) for el in self.neighbors.proba_labels])

        # build the explanation from the neighbors
        if idx_label is None:
            explanations = []
            for label in range(self.neighbors.proba_labels.shape[1]):
                explanations.append(self.learning_process.solve(self.neighbors, label, explanation_size=explanation_size))
        else:
            explanations = [self.learning_process.solve(self.neighbors, idx_label, explanation_size=explanation_size)]
        explanations = self._shape_explanations(explanations,instance)

        return explanations

    def _shape_explanations(self, explanations, series):
        values_per_slice=int(len(series)/len(explanations[0][0]))
        heatmaps=[]
        i=0
        for i in range(0, len(explanations)):
            heatmap = np.zeros_like(series).reshape(-1)
            for value in explanations[i][0]:
                heatmap[i:values_per_slice+i]=np.ones_like((values_per_slice))*value
                i=values_per_slice+i
                
            heatmaps.append(heatmap)
      
        return heatmaps