# %%

from river import metrics

y_true = [0, 1, 2, 2]
y_pred = [
    {0: 0.29450637, 1: 0.34216758, 2: 0.36332605},
    {0: 0.21290077, 1: 0.32728332, 2: 0.45981591},
    {0: 0.42860913, 1: 0.33380113, 2: 0.23758974},
    {0: 0.44941979, 1: 0.32962558, 2: 0.22095463}
]

metric = metrics.CrossEntropy()

for yt, yp in zip(y_true, y_pred):
    metric.update(yt, yp)
    print(metric.get())
# %%
