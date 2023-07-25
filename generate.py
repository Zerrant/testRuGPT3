import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

np.random.seed(42)
torch.manual_seed(42)

def load_tokenizer_and_model(model_name_or_path):
  return GPT2Tokenizer.from_pretrained(model_name_or_path), GPT2LMHeadModel.from_pretrained(model_name_or_path).cuda()

def generate(
    model, tok, text,
    lenght, repetition_penalty=5.0, do_sample=True,
    top_k=50, top_p=1.0, temperature=1,
    num_beams=None,
    no_repeat_ngram_size=3, eos_token_id=50256, pad_token_id=50256
    ):
  input_ids = tok.encode(text, return_tensors="pt").cuda()
  out = model.generate(
      input_ids.cuda(),
      max_length=lenght,
      repetition_penalty=repetition_penalty,
      do_sample=do_sample,
      top_k=top_k,
      top_p=top_p, temperature=temperature,
      num_beams=num_beams, no_repeat_ngram_size=no_repeat_ngram_size,
      eos_token_id=eos_token_id, pad_token_id=pad_token_id
      )
  return list(map(tok.decode, out))

def generation(text, model, lenght):
    tok, model = load_tokenizer_and_model(model)
    generated = generate(model, tok, text+" ", lenght, num_beams=10)

    print(generated[0])
    if "<s>" in generated[0]:

        generated[0] = generated[0].split("<s>")
        return generated[0][0]
    else:
        return generated[0]