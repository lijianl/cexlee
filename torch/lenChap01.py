from __future__ import print_function
import torch


def len_tensors():
    '''
    Tensors 类似于 NumPy 的 ndarrays
    '''
    # Y * X, 生成空的tensor
    m1 = torch.empty(5, 3)
    m2 = torch.rand(5, 3)
    # Numpy的索引
    print(m1[:, 1])
    print(m2[0, 0])


def len_grad():
    '''
    autograd 自动微分
    '''
    pass


if __name__ == '__main__':
    len_tensors()
