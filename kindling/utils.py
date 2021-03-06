import numpy as np
import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
from scipy import signal
import gym
from gym import wrappers
import math
import scipy
import matplotlib.pyplot as plt
from matplotlib import animation
from typing import Optional

color2num = dict(
    gray=30,
    red=31,
    green=32,
    yellow=33,
    blue=34,
    magenta=35,
    cyan=36,
    white=37,
    crimson=38,
)


def colorize(
    string: str,
    color: int,
    bold: Optional[bool] = False,
    highlight: Optional[bool] = False,
):
    """
    Colorize a string.
    This function was originally written by John Schulman.
    """
    attr = []
    num = color2num[color]
    if highlight:
        num += 10
    attr.append(str(num))
    if bold:
        attr.append("1")
    return "\x1b[%sm%s\x1b[0m" % (";".join(attr), string)


def calc_logstd_anneal(n_anneal_cycles: int, anneal_start: float, anneal_end: float, epochs: int) -> np.ndarray:
    """
    Calculate log standard deviation annealing schedule. Can be used in PG algorithms on continuous action spaces.

    Args:
        n_anneal_cycles (int): How many times to cycle from anneal_start to anneal_end over the training epochs.
        anneal_start (float): Starting log standard deviation value.
        anneal_end (float): Ending log standard deviation value.
        epochs (int): Number of training cycles.
    """
    if n_anneal_cycles > 0:
        logstds = np.linspace(anneal_start, anneal_end, num=epochs // n_anneal_cycles)
        for _ in range(n_anneal_cycles):
            logstds = np.hstack((logstds, logstds))
    else:
        logstds = np.linspace(anneal_start, anneal_end, num=epochs)

    return logstds


class NetworkUtils:
    """
    Random utilities for neural networks.
    """
    def __init__(self):
        super(NetworkUtils, self).__init__()

    def conv2d_output_size(self, kernel_size, stride, sidesize):
        return (sidesize - (kernel_size - 1) - 1) // stride + 1

    def squared_error_loss(self, target, actual):
        return (actual - target) ** 2


def save_frames_as_gif(frames, filename=None):
    """
    Save a list of frames as a gif

    This code from this floydhub blog post: https://blog.floydhub.com/spinning-up-with-deep-reinforcement-learning/
    """
    # patch = plt.imshow(frames[0])
    fig = plt.figure()
    plt.axis("off")

    def animate(i):
        patch.set_data(frames[i])

    # anim = animation.FuncAnimation(plt.gcf(), animate, frames = len(frames), interval=50)
    anim = animation.ArtistAnimation(fig, frames, interval=50)
    if filename:
        anim.save(filename, writer="imagemagick")


class NormalizedActions(gym.ActionWrapper):
    """
    Normalize actions for continuous policy

    From here: https://github.com/JamesChuanggg/pytorch-REINFORCE/blob/master/normalized_actions.py
    """

    def _action(self, action):
        action = (action + 1) / 2  # [-1, 1] => [0, 1]
        action *= self.action_space.high - self.action_space.low
        action += self.action_space.low
        return action

    def _reverse_action(self, action):
        action -= self.action_space.low
        action /= self.action_space.high - self.action_space.low
        action = action * 2 - 1
        return action

def _discount_cumsum(x: np.array, discount: float):
    """
    magic from rllab for computing discounted cumulative sums of vectors.
    input:
        vector x,
        [x0,
        x1,
        x2]
    output:
        [x0 + discount * x1 + discount^2 * x2,
        x1 + discount * x2,
        x2]
    """
    return scipy.signal.lfilter([1], [1, float(-discount)], x[::-1], axis=0)[::-1]

def conv2d_output_size(kernel_size, stride, sidesize):
    return (sidesize - (kernel_size - 1) - 1) // stride + 1


def num2tuple(num):
    return num if isinstance(num, tuple) else (num, num)


def conv2d_output_shape(h_w, kernel_size=1, stride=1, pad=0, dilation=1):
    h_w, kernel_size, stride, pad, dilation = num2tuple(h_w), \
        num2tuple(kernel_size), num2tuple(stride), num2tuple(pad), num2tuple(dilation)
    pad = num2tuple(pad[0]), num2tuple(pad[1])
    
    h = math.floor((h_w[0] + sum(pad[0]) - dilation[0]*(kernel_size[0]-1) - 1) / stride[0] + 1)
    w = math.floor((h_w[1] + sum(pad[1]) - dilation[1]*(kernel_size[1]-1) - 1) / stride[1] + 1)
    
    return h, w


def convtransp2d_output_shape(h_w, kernel_size=1, stride=1, pad=0, dilation=1, out_pad=0):
    h_w, kernel_size, stride, pad, dilation, out_pad = num2tuple(h_w), \
        num2tuple(kernel_size), num2tuple(stride), num2tuple(pad), num2tuple(dilation), num2tuple(out_pad)
    pad = num2tuple(pad[0]), num2tuple(pad[1])
    
    h = (h_w[0] - 1)*stride[0] - sum(pad[0]) + dialation[0]*(kernel_size[0]-1) + out_pad[0] + 1
    w = (h_w[1] - 1)*stride[1] - sum(pad[1]) + dialation[1]*(kernel_size[1]-1) + out_pad[1] + 1
    
    return h, w
