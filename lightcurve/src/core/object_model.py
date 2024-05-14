from typing import Optional, Union, List

from pydantic import BaseModel, Field

class ObjectReduced(BaseModel):

    oid :              str
    #ndethist :         int # no
    #ncovhist :         int # no
    #mjdstarthist :     float # no
    #mjdendhist :       float # no
    corrected :        bool
    stellar :          bool
    ndet :             int
    #g_r_max :          float
    #g_r_max_corr :     float
    #g_r_mean :         float
    #g_r_mean_corr :    float
    meanra :           float
    meandec :          float
    #sigmara :          float # no
    #sigmadec :         float # no
    #deltajd :          float # no
    firstmjd :         float
    lastmjd :          float
    #step_id_corr :     str
    #diffpos :          bool
    #reference_change :bool

    pass

