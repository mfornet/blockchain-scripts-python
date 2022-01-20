# %%
from google.cloud import bigquery
import os
import pickle
# %%
data = open('.dat/bigquery_table', 'rb').read()
data = pickle.loads(data)
print(data)

# %%
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/marcelo/gcloud.json'
client = bigquery.Client()
# %%
res = client.query(
    "SELECT * FROM `near-core.bridge_erc20_token.near_withdraw`")
# %%
data = list(res)


# %%
dict(data[0])
# %%
