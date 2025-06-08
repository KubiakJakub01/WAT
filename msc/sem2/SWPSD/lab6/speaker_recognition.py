import os
import tempfile

import torch
import torchaudio
from datasets import load_dataset
from speechbrain.pretrained import SpeakerRecognition


def main():
    dataset = load_dataset("xbgoose/ravdess", split="train")
    item1 = dataset[0]
    item2 = dataset[1]
    verifier = SpeakerRecognition.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        item1_path = os.path.join(temp_dir, "item1.wav")
        item2_path = os.path.join(temp_dir, "item2.wav")
        torchaudio.save(
            item1_path,
            torch.tensor(item1["audio"]["array"]).unsqueeze(0),
            item1["audio"]["sampling_rate"],
        )
        torchaudio.save(
            item2_path,
            torch.tensor(item2["audio"]["array"]).unsqueeze(0),
            item2["audio"]["sampling_rate"],
        )
        score, decision = verifier.verify_files(item1_path, item2_path)
    print(score, decision)


if __name__ == "__main__":
    main()
