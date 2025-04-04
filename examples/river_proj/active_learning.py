# %%
from river_proj import evaluate
from river_proj import active
from river_proj import datasets
from river_proj import feature_extraction
from river_proj import linear_model
from river_proj import metrics

dataset = datasets.SMSSpam()
metric = metrics.Accuracy()
model = (
    feature_extraction.TFIDF(on='body') |
    linear_model.LogisticRegression()
)
model = active.EntropySampler(model, seed=42)

n_samples_used = 0
for x, y in dataset:
    y_pred, ask = model.predict_one(x)
    metric.update(y, y_pred)
    if ask:
        n_samples_used += 1
        model.learn_one(x, y)

metric
# %%
print(f"{n_samples_used} / {dataset.n_samples} = {n_samples_used /
      dataset.n_samples:.2%}")
# %%

evaluate.progressive_val_score(
    dataset=dataset,
    model=model.clone(),
    metric=metric.clone(),
    print_every=1000
)
# %%
