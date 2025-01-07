import torch
import torch.nn as nn

from torch.ao.quantization.observer import ObserverBase
from torch.ao.quantization.fake_quantize import FakeQuantizeBase

from .quantized_modules import QuantizedConv1d, QuantizedConv2d, QuantizedConv3d


class FuseQatConvReLU:
    _conv_nodes = (
        nn.Conv1d,
        nn.Conv2d,
        nn.Conv3d,
        QuantizedConv1d,
        QuantizedConv2d,
        QuantizedConv3d,
    )

    @staticmethod
    def get_module(graph_module, node, tps=None):
        if node.op != 'call_module':
            return None
        mod = graph_module.get_submodule(node.target)
        if tps is None:
            return mod

        if not isinstance(tps, (tuple, list)):
            tps = (tps,)
        if not isinstance(mod, tps):
            return None
        return mod

    @staticmethod
    def apply(graph_module: torch.fx.GraphModule):
        for maybe_relu_node in graph_module.graph.nodes:
            if FuseQatConvReLU.get_module(graph_module, maybe_relu_node, nn.ReLU) is None:
                continue

            maybe_fq_node = maybe_relu_node.args[0]
            if FuseQatConvReLU.get_module(graph_module, maybe_fq_node, (ObserverBase, FakeQuantizeBase)) is None:
                continue
            if len(maybe_fq_node.users) > 1:
                continue

            maybe_conv_node = maybe_fq_node.args[0]
            if FuseQatConvReLU.get_module(graph_module, maybe_conv_node, FuseQatConvReLU._conv_nodes) is None:
                continue
            if len(maybe_conv_node.users) > 1:
                continue

            maybe_fq_node.replace_all_uses_with(maybe_conv_node)
            graph_module.graph.erase_node(maybe_fq_node)

        return torch.fx.GraphModule(graph_module, graph_module.graph)