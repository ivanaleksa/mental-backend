import re
import threading
from abc import ABC, abstractmethod
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from googletrans import Translator
from app.db.enums import EmotionsEnum


class AbstractModel(ABC):
    @abstractmethod
    def _validation(self):
        """This method should validate input data and return preprocessed data"""
        pass

    @abstractmethod
    def _preprocessing(self):
        """This method should preprocess data before sending it to a model"""
        pass

    @abstractmethod
    def predict(self):
        """This method receives data and returns some prediction"""
        pass


class RoBertaModel(AbstractModel):
    emotions = {
        0: "afraid",
        1: "angry",
        2: "anxious",
        3: "ashamed",
        4: "awkward",
        5: "bored",
        6: "calm",
        7: "confused",
        8: "disgusted",
        9: "excited",
        10: "frustrated",
        11: "happy",
        12: "jealous",
        13: "nostalgic",
        14: "proud",
        15: "sad",
        16: "satisfied",
        17: "surprised"
    }

    emotion_to_enum_mapping = {
        "afraid": EmotionsEnum.AFRAID,
        "angry": EmotionsEnum.ANGRY,
        "anxious": EmotionsEnum.ANXIOUS,
        "ashamed": EmotionsEnum.ASHAMED,
        "awkward": EmotionsEnum.AWKWARD,
        "bored": EmotionsEnum.BORED,
        "calm": EmotionsEnum.CALM,
        "confused": EmotionsEnum.CONFUSED,
        "disgusted": EmotionsEnum.DISGUSTED,
        "excited": EmotionsEnum.EXCITED,
        "frustrated": EmotionsEnum.FRUSTRATED,
        "happy": EmotionsEnum.HAPPY,
        "jealous": EmotionsEnum.JEALOUS,
        "nostalgic": EmotionsEnum.NOSTALGIC,
        "proud": EmotionsEnum.PROUD,
        "sad": EmotionsEnum.SAD,
        "satisfied": EmotionsEnum.SATISFIED,
        "surprised": EmotionsEnum.SURPRISED
    }

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=len(self.emotions))
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        self.model.eval()
        self.tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
        self.translator = Translator()

    def _validation(self, text: str) -> bool:
        if re.match(r'^[a-zA-Z0-9\s.,!?\'\"]+$', text):
            return True
        else:
            return False
    
    def _preprocessing(self, text: str) -> dict:
        if not self._validation(text):
            translated = self.translator.translate(text, dest='en').text
        else:
            translated = text
        
        inputs = self.tokenizer(translated, return_tensors="pt", padding=True, truncation=True, max_length=512)
        return inputs

    def predict(self, text: str) -> list[str]:
        inputs = self._preprocessing(text)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1).cpu().numpy()

        emotion_probabilities = {self.emotions[i]: prob * 100 for i, prob in enumerate(probabilities[0])}
        top_3_emotions = sorted(emotion_probabilities.items(), key=lambda item: item[1], reverse=True)[:3]
        
        result = [self.emotion_to_enum_mapping[emotion].value for emotion, _ in top_3_emotions]
        return result


class ThreadSafeModelHandler:
    """This class ensures a separate RoBertaModel instance per thread to avoid thread-safety issues."""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.local = threading.local()

    def get_model(self):
        if not hasattr(self.local, "model"):
            self.local.model = RoBertaModel(self.model_path)
        return self.local.model

    def predict(self, text: str) -> list[str]:
        model = self.get_model()
        return model.predict(text)
