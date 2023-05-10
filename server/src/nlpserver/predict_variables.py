# checking time for one inference
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

import time
import os

import pathlib

from typing import Optional

from events import post_event

MODEL_DIR = pathlib.Path(__file__).parents[0].joinpath("models")

MODEL = None
TOKENIZER = None
DEVICE = None

MODEL_NAME: str = "sangam101/hpc"


def initalize_model(model_name: str = MODEL_NAME, use_local: bool = True):
    location_str = "locally" if use_local else "from huggingface"
    post_event("log", f"Initializing {model_name} {location_str}")

    global MODEL, TOKENIZER, DEVICE

    copy_of_model_name = model_name

    if use_local:
        model_name = str(MODEL_DIR.joinpath(pathlib.Path(model_name).__str__()))
        post_event("log", f"Using model available at location {model_name}")

        if not os.path.exists(model_name):
            post_event(
                "log",
                f"The model {copy_of_model_name} doesn't exist locally at {model_name}, so downloading from huggingface.",
            )

            model_name = copy_of_model_name
    else:
        post_event("log", f"Downloading model available at location {model_name}")

    MODEL = AutoModelForSeq2SeqLM.from_pretrained(
        model_name, cache_dir=MODEL_DIR.__str__(), force_download=False
    )
    TOKENIZER = AutoTokenizer.from_pretrained(
        model_name, cache_dir=MODEL_DIR.__str__(), force_download=False
    )

    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    MODEL.to(DEVICE)

    post_event(
        "log", f"Setup:: Model: {MODEL} \n Tokenizer: {TOKENIZER} \n Device: {DEVICE}"
    )

    # saving the model for later use
    model_name = str(MODEL_DIR.joinpath(pathlib.Path(model_name).__str__()))
    post_event("log", f"Saving the model to {model_name}")
    MODEL.save_pretrained(model_name, from_pt=True)
    TOKENIZER.save_pretrained(model_name, from_pt=True)


def get_variable_name(comment: str, **kwargs) -> Optional[str]:
    """
    Returns space separated variable parts if successful else returns None
    """
    global TOKENIZER, MODEL, DEVICE

    if TOKENIZER is None or MODEL is None:
        initalize_model()

    if TOKENIZER is not None and MODEL is not None and DEVICE is not None:
        start_time = time.time()
        # --------------------------------------INFERENCE_START-------------------------------------------------------------
        encoded_input = TOKENIZER(comment, return_tensors="pt").to(DEVICE)

        summary_ids = MODEL.generate(
            encoded_input["input_ids"],
            num_beams=4,
            max_length=100,
            early_stopping=True,
            use_cache=True,
            do_sample=True,
            kwargs=kwargs
        ).to(DEVICE)

        output_variable_name = TOKENIZER.decode(
            summary_ids[0], skip_special_tokens=True
        )
        # --------------------------------------INFERENCE_END---------------------------------------------------------------
        end_time = time.time()

        post_event("log", f"Input Comment: {comment}")
        post_event("log", f"Variable Name: {output_variable_name}")
        post_event(
            "log", f"Time taken: {end_time - start_time} seconds, Device Used: {DEVICE}"
        )

        return output_variable_name

    else:
        if MODEL is None:
            post_event("log", "Error in model configuration.")

        if TOKENIZER is None:
            post_event("log", "Error in tokenizer configuration.")

        if DEVICE is None:
            post_event("log", "Error in device configuration.")

        return None
