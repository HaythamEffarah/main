# Copyright 2020, General Electric Company. All rights reserved. See https://github.com/xcist/code/blob/master/LICENSE

import numpy as np
import os
from catsim.CommonTools import *
import matplotlib.pyplot as plt

# This is a simplified kernel based scatter model, will have roughly 15% SPR for 35-cm water phantom, 120 kVp, 40-mm beam width.
def Scatter_ConvolutionModel(cfg, viewId, subViewId):
    # Get scatter kernel
    if viewId == cfg.sim.startViewId and subViewId == 0:
        if cfg.physics.scatterKernelCallback:
            cfg.scatter_kernel = feval(cfg.physics.scatterKernelCallback, cfg)
        else:
            cfg.scatter_kernel = get_scatter_kernel()
            
    # Scatter is low frequency signal and computational expensive, we only calculate it at the first subview.
    if subViewId == 0:
        prep = -np.log(cfg.thisSubView.sum(1)/cfg.detFlux.sum(1))
        if not hasattr(cfg.physics, "scatterScaleFactor"):
            cfg.physics.scatterScaleFactor = 1
        sc_preConv = cfg.thisSubView.sum(1)*prep*0.025*cfg.physics.scatterScaleFactor
        sc_preConv = sc_preConv.reshape(cfg.scanner.detectorColCount, cfg.scanner.detectorRowCount)
        sc_conv = conv2(sc_preConv, cfg.scatter_kernel, 'same')
        
        sc_conv = sc_conv.reshape(sc_conv.size,1)
        spec = cfg.thisSubView.mean(0)
        spec /= spec.sum()
        spec = spec.reshape(1,spec.size)
        sc_conv_spec = sc_conv @ spec
        
        cfg.scatter_view = sc_conv_spec
        
    cfg.thisSubView += cfg.scatter_view
    
    return cfg

def get_scatter_kernel():
    scatterDataFile = "scatter_kernel.dat"
    if not os.path.isfile(scatterDataFile):
        scatterDataFile = get_path().scatter + '/scatter_kernel.dat'
    h = rawread(scatterDataFile, [49,65], 'float');
    h = h/np.sum(h)    
    return h
    