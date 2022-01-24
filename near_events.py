"""
Get all events of type deposit and withdraw from NEAR using bigquery.

Need to log in with google cloud to use this script.
"""

from lib import persist_to_file
from pprint import pprint
from google.cloud import bigquery


def main():
    client = bigquery.Client()

    @persist_to_file('.dat/bigquery_table')
    def get_all(table_id):
        DEPOSIT_QUERY = f"SELECT * FROM `near-core.bridge_erc20_token.{table_id}`"
        query_job = client.query(DEPOSIT_QUERY)  # Make an API request.
        return list([dict(x) for x in query_job])

    pprint(get_all('near_withdraw')[0])
    pprint(get_all('near_deposit_transaction')[0])


if __name__ == "__main__":
    main()
