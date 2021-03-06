import time
import sklearn.svm
import numpy as np
import random
import matplotlib.pyplot as plt


from frameworks.CPLELearning import CPLELearningModel
from methods import scikitTSVM

kernel = "rbf"

# number of data points
N = 60
supevised_data_points = 4

# generate data
meandistance = 2

s = np.random.random()
cov = [[s, 0], [0, s]]
# some random Gaussians
gaussians = 6 #np.random.randint(4, 7)
Xs = np.random.multivariate_normal([np.random.random()*meandistance, np.random.random()*meandistance], cov, (N/gaussians,))
for i in range(gaussians-1):
    Xs = np.vstack(( Xs, np.random.multivariate_normal([np.random.random()*meandistance, np.random.random()*meandistance], cov, (N/gaussians,)) ))

# cut data into XOR
ytrue = ((Xs[:, 0] < np.mean(Xs[:, 0]))*(Xs[:, 1] < np.mean(Xs[:, 1])) + (Xs[:, 0] > np.mean(Xs[:, 0]))*(Xs[:, 1] > np.mean(Xs[:, 1])))*1

ys = np.array([-1]*N)
sidx = random.sample(np.where(ytrue == 0)[0], supevised_data_points/2)+random.sample(np.where(ytrue == 1)[0], supevised_data_points/2)
ys[sidx] = ytrue[sidx]

Xsupervised = Xs[ys!=-1, :]
ysupervised = ys[ys!=-1]

plt.figure()
cols = [np.array([1,0,0]),np.array([0,1,0])] # colors

# loop through and compare methods     
for i in range(4):
    plt.subplot(2,2,i+1)
    plt.hold(True)
    
    t1=time.time()
    # train model
    if i == 0:
        lbl = "Purely supervised SVM:"
        model = sklearn.svm.SVC(kernel=kernel, probability=True)
        model.fit(Xsupervised, ysupervised)
    else:
        if i==1:
            lbl =  "S3VM (Gieseke et al. 2012):"
            model = scikitTSVM.SKTSVM(kernel=kernel)
        elif i == 2:
            lbl = "CPLE(pessimistic) SVM:"
            model = CPLELearningModel(sklearn.svm.SVC(kernel=kernel, probability=True), predict_from_probabilities=True)
        elif i == 3:
            lbl = "CPLE(optimistic) SVM:"
            CPLELearningModel.pessimistic = False
            model = CPLELearningModel(sklearn.svm.SVC(kernel=kernel, probability=True), predict_from_probabilities=True)
        model.fit(Xs, ys.astype(int))
    print ""
    print lbl
    print "Model training time: ", round(time.time()-t1, 3)

    # predict, and evaluate
    pred = model.predict(Xs)
    
    acc = np.mean(pred==ytrue)
    print "accuracy:", round(acc, 3)
    
    # plot probabilities
    [minx, maxx] = [np.min(Xs[:, 0]), np.max(Xs[:, 0])]
    [miny, maxy] = [np.min(Xs[:, 1]), np.max(Xs[:, 1])]
    gridsize = 100
    xx = np.linspace(minx, maxx, gridsize)
    yy = np.linspace(miny, maxy, gridsize).T
    xx, yy = np.meshgrid(xx, yy)
    Xfull = np.c_[xx.ravel(), yy.ravel()]
    probas = model.predict_proba(Xfull)
    plt.imshow(probas[:, 1].reshape((gridsize, gridsize)), extent=(minx, maxx, miny, maxy), origin='lower')
    
    # plot decision boundary
    try:
        if i > 1:
            plt.contour((probas[:, 0]<np.average(probas[:, 0])).reshape((gridsize, gridsize)), extent=(minx, maxx, miny, maxy), origin='lower')
        else:
            plt.contour(model.predict(Xfull).reshape((gridsize, gridsize)), extent=(minx, maxx, miny, maxy), origin='lower')
    except:
        print "contour failed"
    
    # plot data points
    #P = np.max(model.predict_proba(Xs), axis=1)
    P = pred
    plt.scatter(Xs[:, 0], Xs[:,1], c=ytrue, s=(ys>-1)*300+100, linewidth=1, edgecolor=[cols[p]*P[p] for p in model.predict(Xs).astype(int)], cmap='hot')
    plt.scatter(Xs[ys>-1, 0], Xs[ys>-1,1], c=ytrue[ys>-1], s=300, linewidth=1, edgecolor=[cols[p]*P[p] for p in model.predict(Xs).astype(int)], cmap='hot')
    plt.title(lbl + str(round(acc, 2)))
    plt.hold(False)
    
plt.show(block=True)
