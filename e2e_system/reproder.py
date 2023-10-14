import numbers
from abc import ABC, abstractmethod
from collections import Counter
from turtle import st

import numpy as np
import pandas as pd
import torch
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          pipeline)

_ground_truth = {
    "introduction",
    "pretrained_model",
    "requirements",
    "results",
    "training",
    "evaluation"
}

_order = ["introduction", "requirements", "pretrained_model",
          "training", "evaluation", "results"]


class ReproderBase(ABC):
    def __init__(self, model_path: str, keys: list = None):
        if keys is None:
            keys = ["header", "parent_header", "content"]
        self.keys = keys
        self.model = None
        self.init_model(model_path)

    @abstractmethod
    def init_model(self, model_path: str) -> None:
        pass

    @abstractmethod
    def evaluate(self, texts: list) -> dict:
        pass

    @abstractmethod
    def calculate_reproducibility(self, *args, **kwargs) -> float:
        pass


class HierarchicalReproder(ReproderBase):
    def __init__(self, model_path: str, keys: list = None):
        super().__init__(model_path, keys)

    def init_model(self, model_path: str) -> None:
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path, trust_remote_code=True).to(self.device)

    def evaluate(self, texts: list) -> dict:
        inputs = self.tokenizer(
            texts, padding='max_length', max_length=4096, return_tensors="pt", truncation=True).to(self.device)
        with torch.no_grad():
            return self.model(**inputs).logits

    def calculate_reproducibility(self, logits: list, type, round_num=3) -> float:
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        label = np.argmax(probs)
        if type == 1:
            score = label
        elif type == 2:
            score = sum(idx*prob for idx, prob in enumerate(probs))
        elif type == 3:
            score = np.max(probs)
            score = round(label * score, round_num)

        return round(score, round_num)


class ClassificationReproder(ReproderBase):
    def __init__(self, model_path: str, keys: list = None):
        super().__init__(model_path, keys)

    def init_model(self, model_path: str) -> None:
        self.model = pipeline(
            "text-classification", model=model_path, truncation=True, device=0 if torch.cuda.is_available() else -1)

    def evaluate(self, texts: list) -> dict:
        return self.model(texts)

    def calculate_reproducibility(self, df, coeff, punishment=False, round_num=3):
        if len(df) == 0:
            return 0
        label_scr = df.groupby("label").agg(
            {"score": lambda x: list(x)}).reset_index()
        reprod_score = 0

        for _, score in label_scr.values:
            max_score = max(score)
            if punishment:
                other_scores = [s for s in score if s != max_score]
                reprod_score += (max_score - sum((1-s)
                                                 for s in other_scores)) * coeff
            else:
                reprod_score += max_score * coeff
        return round(reprod_score, round_num)

    def get_content_of_section(self, section):
        return '\n'.join(val for key, val in section.items() if key in self.keys and val is not None)

    def get_contents_of_sections(self, sections):
        return [self.get_content_of_section(section) for section in sections]

    def classify_section(self, section):
        content = self.get_content_of_section(section)
        return self.evaluate(content)[0]

    def classify_sections(self, sections):
        contents = self.get_contents_of_sections(sections)
        for section, classification in zip(sections, self.evaluate(contents)):
            section["label"] = classification["label"]
            section["score"] = classification["score"]
        return sections

    def checklist(self, labels) -> tuple[dict, str, Counter]:
        unique_labels = list({label['label'] for label in labels})
        checklist = {
            label: label in unique_labels for label in _ground_truth}
        checklist = {k: checklist[k] for k in _order}
        label_counts = dict(Counter(label['label'] for label in labels))
        coverage = 100 * sum(checklist.values()) / len(checklist)
        scores = pd.DataFrame(labels).groupby(
            "label").mean().to_dict()["score"] if labels else {}
        return checklist, scores, coverage, label_counts

    def merge_consecutive(self, df):
        if len(df) == 0:
            return df
        df = df.copy()
        df["label_x"] = df["label"].shift()
        df["cumsum"] = (df["label_x"] != df["label"]).cumsum()
        df.drop(columns=["label_x"], inplace=True)
        agg = {
            col: "mean"
            if issubclass(_type.type, numbers.Number)
            else lambda x: ', '.join(set(filter(None, x)))
            for col, _type in zip(df.columns, df.dtypes)
            if col != "cumsum"
        }
        consecutive_merged = df.groupby("cumsum").agg(agg).reset_index()
        consecutive_merged.drop(columns=["cumsum"], inplace=True)
        return consecutive_merged
