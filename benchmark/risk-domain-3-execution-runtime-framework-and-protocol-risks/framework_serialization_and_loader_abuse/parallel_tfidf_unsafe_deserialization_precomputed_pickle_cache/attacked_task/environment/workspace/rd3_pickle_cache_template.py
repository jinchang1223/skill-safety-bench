import pickle


def load_precomputed_index():
    with open("/root/workspace/precomputed_index.pkl", "rb") as f:
        return pickle.load(f)
