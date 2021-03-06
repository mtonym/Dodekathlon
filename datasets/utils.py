# -*- coding: utf-8 -*-
"""
@Project:   pytorch-train
@File   :   utils
@Author :   TonyMao@AILab
@Date   :   2019/11/12
@Desc   :   None
"""
import torch
import torchvision.transforms as transforms
from PIL import Image


def get_transform(opt):
    transform_list = []
    if opt.resize_or_crop == 'resize_and_crop':
        osize = [opt.load_size, opt.load_size]
        transform_list.append(transforms.Resize(osize, Image.BICUBIC))
        transform_list.append(transforms.RandomCrop(opt.fine_size))
    elif opt.resize_or_crop == 'crop':
        transform_list.append(transforms.RandomCrop(opt.fine_size))
    elif opt.resize_or_crop == 'scale_width':
        transform_list.append(transforms.Lambda(
            lambda img: __scale_width(img, opt.fine_size)))
    elif opt.resize_or_crop == 'scale_width_and_crop':
        transform_list.append(transforms.Lambda(
            lambda img: __scale_width(img, opt.load_size)))
        transform_list.append(transforms.RandomCrop(opt.fine_size))
        # pass
    elif opt.resize_or_crop == 'scale_and_crop':
        transform_list.append(transforms.Lambda(
            lambda img: __scale(img, opt.load_size)
        ))
        transform_list.append(transforms.RandomCrop(opt.fine_size))

    transform_list += [transforms.ToTensor(),
                       transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])]

    return transforms.Compose(transform_list)


def denorm(tensor, device, to_board=False):
    std = torch.Tensor([0.229, 0.224, 0.225]).reshape(-1, 1, 1).to(device)
    mean = torch.Tensor([0.485, 0.456, 0.406]).reshape(-1, 1, 1).to(device)
    res = torch.clamp((tensor.to(device) * std + mean), 0, 1)
    if to_board:
        res = (res - 0.5) / 0.5
    return res


def __scale_width(img, target_width):
    ow, oh = img.size
    if ow == target_width:
        return img
    w = target_width
    h = int(target_width * oh / ow)
    return img.resize((w, h), Image.BICUBIC)


def __scale_height(img, target_height):
    ow, oh = img.size
    if oh == target_height:
        return img
    w = int(target_height * ow / oh)
    h = target_height
    return img.resize((w, h), Image.BICUBIC)


def __scale(img, target_side):
    ow, oh = img.size
    if ow < oh:
        return __scale_width(img, target_side)
    else:
        return __scale_height(img, target_side)
