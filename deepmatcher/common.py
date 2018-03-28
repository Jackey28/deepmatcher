import torch
from collections import namedtuple
from torch.autograd import Variable
import pdb


AttrTensor_ = namedtuple('AttrTensor', ['data', 'lengths', 'word_probs', 'pc'])


class AttrTensor(AttrTensor_):

    @staticmethod
    def __new__(cls, *args, **kwargs):
        if len(kwargs) == 0:
            return super(AttrTensor, cls).__new__(cls, *args)
        else:
            name = kwargs['name']
            attr = kwargs['attr']
            train_dataset = kwargs['train_dataset']
            if isinstance(attr, tuple):
                data = attr[0]
                lengths = attr[1]
            else:
                data = attr
                lengths = None
            word_probs = None
            if 'word_probs' in train_dataset.metadata:
                raw_word_probs = train_dataset.metadata['word_probs'][name]
                word_probs = torch.Tensor([[raw_word_probs[w] for w in b] for b in data.data])
                if data.is_cuda:
                    word_probs = word_probs.cuda()
            pc = None
            if 'pc' in train_dataset.metadata:
                pc = torch.Tensor(train_dataset.metadata['pc'][name])
                if data.is_cuda:
                    pc = pc.cuda()
            return AttrTensor(data, lengths, word_probs, pc)

    @staticmethod
    def from_old_metadata(data, old_attrtensor):
        return AttrTensor(data, *old_attrtensor[1:])


class MatchingBatch(object):

    def __init__(self, input, train_dataset):
        copy_fields = train_dataset.all_text_fields
        for name in copy_fields:
            setattr(self, name,
                    AttrTensor(
                        name=name, attr=getattr(input, name),
                        train_dataset=train_dataset))
        for name in [train_dataset.label_field, train_dataset.id_field]:
            if name is not None:
                setattr(self, name, getattr(input, name))
