import json

import torch
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline


class GroundTruthLabellingHelper:
    def __init__(self, model_name='all-mpnet-base-v2'):
        device = "cuda" if torch.cuda.is_available() else "cpu"

        model = SentenceTransformer(model_name, device=device)
        self.model = model
        ground_truth = json.load(
            open('data/constants/sections_ground_truth.json'))
        self.create_group_definition_embeddings(ground_truth)

    def create_group_definition_embeddings(self, group_definitions):
        self.group_definitions = group_definitions
        self.group_definition_embeddings = {group: self.model.encode(
            definition, convert_to_tensor=True) for group, definition in group_definitions.items()}

    def get_similarity_with_embeddings(self, sentence):
        if not hasattr(self, 'group_definition_embeddings'):
            raise AttributeError(
                'You need to create group definition embeddings first!')
        sentence_embedding = self.model.encode(
            sentence, convert_to_tensor=True)
        return {group: util.pytorch_cos_sim(sentence_embedding, group_definition_embedding) for group, group_definition_embedding in self.group_definition_embeddings.items()}

    def get_most_similar_group(self, sentence):
        similarities = self.get_similarity_with_embeddings(sentence)
        max_group = max(similarities, key=similarities.get)
        return max_group, similarities[max_group].item()


class ZeroShotLabellingHelper:
    def __init__(self, model_name="facebook/bart-large-mnli"):
        device = 0 if torch.cuda.is_available() else -1

        model = pipeline("zero-shot-classification",
                         model=model_name, device=device)
        self.model = model
        self.labels = list(json.load(
            open('data/constants/sections_ground_truth.json')).keys())

    def get_most_likely_label(self, text):
        model_dict = self.model(text, self.labels, multi_label=True)
        result_dict = dict(
            zip(model_dict.get('labels'), model_dict.get('scores')))
        max_score_label = max(result_dict, key=result_dict.get)
        return max_score_label, result_dict[max_score_label]
