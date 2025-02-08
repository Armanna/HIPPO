import yaml
from utils.extract import Extract
from utils.process import Process
from utils.validation import ClaimEvent, RevertEvent
from utils.my_logging import logging 

with open('configs.yaml', 'r') as file:
    configs = yaml.safe_load(file)

source = configs['source']


def main():
    #GOAL 1
    pharmacies = Extract(source['pharmacy']['path']).read_pharmacy_data()
    claims = Extract(source['claim']['path'], ClaimEvent).read_and_validate_events()
    reverts = Extract(source['revert']['path'], RevertEvent).read_and_validate_events()

    PHARMACY = Process(pharmacies, claims, reverts)
    pharmacy_data = PHARMACY.get_pharmacy_data()
    logging.info("GOAL 1 IS DONE: Data is extracted")

    # GOAL 2
    PHARMACY.get_pharmacy_metrics(pharmacy_data)
    logging.info("GOAL 2 IS DONE. Check output_data\metrics_output.json")

    # GOAL 3
    PHARMACY.make_recommendations(pharmacy_data)
    logging.info("GOAL 3 IS DONE. Check output_data\drug_unit_prices_per_chain.json")


    # GOAL 4
    PHARMACY.get_most_common_quantity(pharmacy_data)
    logging.info("GOAL 4 IS DONE. Check output_data\most_common_quantity_prescribed.json")


if __name__ == "__main__":
    
    logging.info("APPLICATION STARTED ========================================")
    main()
    logging.info("APPLICATION COMPLETED ========================================")


