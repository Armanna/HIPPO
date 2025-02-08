import json
import numpy as np
import pandas as pd
from typing import List
from collections import Counter
from utils.validation import ClaimEvent, RevertEvent


class Process:
    def __init__(self, pharmacy_data:set, claim_data:List[ClaimEvent], revert_data:List[RevertEvent]):
        self.pharmacy_data = pharmacy_data
        self.claim_data = claim_data
        self.revert_data = revert_data

    def get_pharmacy_data(self): 
        # Pharmacy dataframe
        pharmacy_df = pd.DataFrame(self.pharmacy_data.items(), columns=["npi", "chain"])
    
        # ClaimEvent dataframe
        claim_dict = [claim.model_dump() for claim in self.claim_data]
        claim_df = pd.DataFrame(claim_dict)

        # RevertEvent dataframe
        revert_dict = [revert.model_dump() for revert in self.revert_data]
        revert_df = pd.DataFrame(revert_dict)

        claims_pharmacy_df = pd.merge(claim_df, pharmacy_df, how='inner', on='npi')
        final_df = pd.merge(claims_pharmacy_df, revert_df, how='left', left_on='id', right_on='claim_id')
        final_df.drop(columns=['id_y', 'claim_id'], inplace=True)
        final_df.rename(columns={'id_x':'id', 'timestamp_x': 'claim_timestamp', 'timestamp_y': 'revert_timestamp', }, inplace=True)
        final_df['unit_price'] = np.where(final_df['quantity'] == 0, np.nan, final_df['price'] / final_df['quantity'])

        final_df['price'] = final_df['price'].astype(float).round(2)
        final_df['unit_price'] = final_df['unit_price'].astype(float).round(2)
        final_df['quantity'] = final_df['unit_price'].astype(float).round(2)

        return final_df
    

    def get_pharmacy_metrics(self, df:pd.DataFrame):
        pharmacy_data = df.copy()


        # Step 2: Group by 'npi' and 'ndc' and calculate metrics
        metrics_df = pharmacy_data.groupby(['npi', 'ndc']).agg(
            fills=('id', 'count'),  # Count of claims
            reverted=('revert_timestamp', lambda x: x.notna().sum()),  # Count of reverts
            avg_price=('unit_price', 'mean'),  # Average unit price
            total_price=('price', 'sum')  # Total price
        ).reset_index()

        metrics_df['avg_price'] = metrics_df['avg_price'].astype(float).round(2)
        metrics_df['total_price'] = metrics_df['total_price'].astype(float).round(2)

        # Step 3: Convert the DataFrame to a list of dictionaries in the desired format
        metrics_list = metrics_df.to_dict(orient='records')


        # Step 4: Write the result to a JSON file
        output_file = 'output_data/metrics_output.json'
        with open(output_file, 'w') as f:
            json.dump(metrics_list, f, indent=4)


    def make_recommendations(self, df:pd.DataFrame):
        pharmacy_data = df.copy()
        # Step 1: Group by 'ndc' (drug) and 'chain' (pharmacy chain) and calculate the average unit price
        chain_avg_price = pharmacy_data.groupby(['ndc', 'chain']).agg(
            avg_price=('unit_price', 'mean')  
        ).reset_index()

        chain_avg_price['avg_price'] = chain_avg_price['avg_price'].astype(float).round(2)

        # Step 2: Sort by 'ndc' and 'avg_price' to identify chains that charge less on average
        chain_avg_price_sorted = chain_avg_price.sort_values(by=['ndc', 'avg_price'])

        # Step 3: Organize the data in the required format (top 2 chains per drug)
        output = []
        for ndc, group in chain_avg_price_sorted.groupby('ndc'):
            top_chains = group.head(2)
            chain_list = top_chains[['chain', 'avg_price']].to_dict(orient='records')
            
            # Append to the final output
            output.append({
                'ndc': ndc,
                'chain': chain_list
            })

        # Step 4: Write the result to a JSON file
        output_file = 'output_data/drug_unit_prices_per_chain.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=4)


    def get_most_common_quantity(self, df:pd.DataFrame):
        pharmacy_data = df.copy()

        # Step 1: Calculate the most common prescribed quantity per drug (ndc)
        most_common_quantity = pharmacy_data.groupby('ndc')['quantity'].apply(list).reset_index()        

        # Step 2: Format the result in the required structure
        output = []
        for _, row in most_common_quantity.iterrows():
            # Count occurrences of each quantity
            quantity_counts = Counter(row['quantity'])
            
            # Get the 5 most common quantities (quantity, count)
            most_common_quantities = [quantity for quantity, _ in quantity_counts.most_common(5)]
            
            # Append the result in the required format
            output.append({
                'ndc': row['ndc'],
                'most_prescribed_quantity': most_common_quantities
            })

        # Step 3: Write the result to a JSON file
        output_file = 'output_data/most_common_quantity_prescribed.json'
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=4)



    