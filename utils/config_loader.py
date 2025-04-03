import json

def load_config_for_company(company_name: str) -> dict:
    with open("config/company_config.json") as f:
        all_configs = json.load(f)
        print(all_configs)
        return all_configs.get(company_name.lower())
    
def load_config_for_filter() -> dict:
    with open("config/filter_config.json") as f:
        all_configs = json.load(f)
        return all_configs

