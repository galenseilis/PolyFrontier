def load_models():
    import json
    with open("app/data/models.json", mode='r', encoding='utf-8') as f:
        models_dict = json.load(f)
        for k, v in models_dict.items():
            yield k, v
